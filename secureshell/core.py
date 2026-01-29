"""
SecureShell Core (Production Grade).
The main entry point for the library.
"""
import asyncio
import os
import platform
import shlex
from typing import List, Optional, Dict, Any, Union
import structlog

from secureshell.models import (
    RiskTier, 
    GatekeeperDecision, 
    ExecutionResult, 
    GatekeeperResponse,
    CheckResult
)
from secureshell.config import SecureShellConfig
from secureshell.risk_engine import RiskClassifier
from secureshell.sandbox import SandboxValidator
from secureshell.gatekeeper import GatekeeperLLM
from secureshell.audit import AuditLogger
from secureshell.providers.base import BaseLLMProvider
from secureshell.providers.openai import OpenAI

logger = structlog.get_logger()

class SecureShell:
    """
    A secure wrapper for shell execution.2
    
    Usage:
        shell = SecureShell()
        result = await shell.execute("rm -rf /", "cleaning up")
    """
    
    def __init__(
        self,
        provider: BaseLLMProvider = None,
        config: SecureShellConfig = None,
        template: str = None,
        allowed_paths: List[str] = None, # Overrides config
        blocked_paths: List[str] = None, # Overrides config
        os_info: str = None
    ):
        """
        Args:
            provider: Custom LLM provider instance.
            config: Configuration object. If None, loads from env/.env.
            template: Security template name ('paranoid', 'development', 'production', 'ci_cd')
            allowed_paths: Optional override for allowed paths.
            blocked_paths: Optional override for blocked paths.
            os_info: Operational System description.
        """
        self.config = config or SecureShellConfig.load()
        
        # Apply security template if specified
        if template:
            from secureshell.templates import get_template
            tmpl = get_template(template)
            logger.info("security_template_loaded", template=template)
            
            # Apply template allowlist/blocklist if not already set
            if not self.config.allowlist:
                self.config.allowlist = tmpl.allowlist
            if not self.config.blocklist:
                self.config.blocklist = tmpl.blocklist
        
        # Initialize components
        self.risk_classifier = RiskClassifier()
        
        # Paths: Args > Config > Defaults
        # Note: In a real app, config might have these list fields too. 
        # For now we stick to simple config or explicit args.
        paths = allowed_paths or [os.getcwd()]
        
        self.sandbox = SandboxValidator(
            allowed_paths=paths, 
            blocked_paths=blocked_paths
        )
        
        self.audit_logger = AuditLogger(
            log_path=self.config.audit_log_path,
            queue_size=self.config.audit_queue_size
        )
        
        # Setup Provider
        if provider:
            self.provider = provider
        else:
            # Factory logic based on config
            if self.config.provider == "openai":
                if self.config.openai_api_key:
                    self.provider = OpenAI(
                        api_key=self.config.openai_api_key
                    )
                else:
                    logger.warning("config_missing_key", provider="openai")
                    self.provider = None
            else:
                logger.warning("unknown_provider", provider=self.config.provider)
                self.provider = None

        if self.provider:
            self.gatekeeper = GatekeeperLLM(self.provider)
        else:
            self.gatekeeper = None
            logger.warning("gatekeeper_disabled", reason="No valid provider configured")
        
        self.os_info = os_info or self.config.environment + " " + platform.system()

    async def handle_tool_call(self, tool_call) -> dict:
        """
        Handle a tool call from an LLM (e.g., OpenAI).
        Parses the arguments, executes via SecureShell, and returns a
        ready-to-use message dict for the LLM conversation.
        
        Args:
            tool_call: The raw tool_call object from OpenAI/Anthropic.
            
        Returns:
            A dict formatted as a 'tool' role message.
        """
        import json
        
        # Parse arguments from LLM
        try:
            args = json.loads(tool_call.function.arguments)
        except (json.JSONDecodeError, AttributeError) as e:
            return {
                "role": "tool",
                "tool_call_id": getattr(tool_call, 'id', 'unknown'),
                "content": json.dumps({"success": False, "error": f"Failed to parse arguments: {e}"})
            }

        command = args.get("command", "")
        reasoning = args.get("reasoning", "")

        # Execute via SecureShell
        result = await self.execute(command=command, reasoning=reasoning)

        # Format response
        return {
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": json.dumps({
                "success": result.success,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "denial_reason": result.denial_reason
            })
        }

    async def execute(
        self, 
        command: str, 
        reasoning: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> ExecutionResult:
        """
        Execute a command securely.
        """
        context = context or {}
        context["os"] = self.os_info
        
        logger.info("exec_start", command=command)

        # 1. Sandbox Validation
        sandbox_res = self.sandbox.validate_command(command)
        if not sandbox_res.passed:
            result = self._create_blocked_result(command, "Sandbox Violation", sandbox_res.reason, RiskTier.BLOCKED)
            await self._audit(command, reasoning, context, result)
            return result

        # 2. Config Policy Check (Allowlist/Blocklist)
        # Extract command type (first word) for matching
        command_type = None
        try:
            parsed = shlex.split(command)
            if parsed:
                command_type = parsed[0]
        except ValueError:
            # If shlex fails (e.g., unmatched quotes), extract first word manually
            command_type = command.split()[0] if command.split() else None
        
        # Check blocklist first
        for pattern in self.config.blocklist:
            if command_type and command_type == pattern:
                result = self._create_blocked_result(
                    command, 
                    "Config Blocked", 
                    f"Command type '{command_type}' matches blocklist pattern: {pattern}", 
                    RiskTier.BLOCKED
                )
                await self._audit(command, reasoning, context, result)
                return result
                
        # Check allowlist
        for pattern in self.config.allowlist:
            if command_type and command_type == pattern:
                logger.info("config_allow", pattern=pattern, command_type=command_type)
                result = await self._run_command(command)
                result.risk_tier = RiskTier.GREEN # Treat as green
                await self._audit(command, reasoning, context, result)
                return result

        # 3. Risk Classification
        risk_tier = self.risk_classifier.classify(command)
        logger.info("risk_assessed", tier=risk_tier)

        # 3. Policy Check
        if risk_tier == RiskTier.BLOCKED:
            result = self._create_blocked_result(command, "Blocked Pattern", "Command matches blocked pattern", risk_tier)
            await self._audit(command, reasoning, context, result)
            return result

        if risk_tier == RiskTier.GREEN:
            # Auto-allow
            logger.info("auto_allow", tier="GREEN")
            result = await self._run_command(command) # Uses config limits
            result.risk_tier = risk_tier
            await self._audit(command, reasoning, context, result)
            return result

        # Yellow/Red -> Gatekeeper calls
        if not self.gatekeeper:
             # Fail closed
             msg = "No gatekeeper configured for high-risk command"
             result = self._create_blocked_result(command, "Configuration Error", msg, risk_tier)
             await self._audit(command, reasoning, context, result)
             return result

        gatekeeper_res = await self.gatekeeper.assess(command, reasoning, risk_tier, context)
        logger.info("gatekeeper_decided", decision=gatekeeper_res.decision.value, reason=gatekeeper_res.explanation)
        
        if gatekeeper_res.decision == GatekeeperDecision.DENY:
            # Explicitly denied by gatekeeper
            result = ExecutionResult(
                success=False,
                denial_reason=gatekeeper_res.explanation,
                risk_tier=risk_tier,
                gatekeeper_response=gatekeeper_res
            )
            await self._audit(command, reasoning, context, result)
            return result
        
        if gatekeeper_res.decision == GatekeeperDecision.CHALLENGE:
            # Gatekeeper needs clarification
            result = ExecutionResult(
                success=False,
                denial_reason=f"Clarification needed: {gatekeeper_res.required_clarification or gatekeeper_res.explanation}",
                risk_tier=risk_tier,
                gatekeeper_response=gatekeeper_res
            )
            await self._audit(command, reasoning, context, result)
            return result

        # 4. Execution (gatekeeper allowed)
        result = await self._run_command(command)
        result.risk_tier = risk_tier
        result.gatekeeper_response = gatekeeper_res
        
        await self._audit(command, reasoning, context, result)
        
        # DEBUG MODE: Print summary
        if self.config.debug_mode:
            self._print_debug_summary(command, reasoning, risk_tier, result)
            
        return result

    def _print_debug_summary(self, cmd, reasoning, risk, result: ExecutionResult):
        """Print a user-friendly debug summary to stdout."""
        from pprint import pformat
        
        print("\n" + "="*60)
        print("[SecureShell Debug]")
        print("="*60)
        
        # Determine decision status
        if result.denial_reason:
            decision = "[BLOCKED]"
        elif result.success:
            decision = "[ALLOWED]"
        else:
            decision = "[ALLOWED (execution failed)]"
        
        debug_data = {
            "Command": cmd,
            "Reasoning": reasoning,
            "Risk Tier": risk.value,
            "Decision": decision,
        }
        
        if result.success:
            debug_data["Output"] = result.stdout.strip()[:200] + "..." if len(result.stdout.strip()) > 200 else result.stdout.strip()
            if result.stderr:
                debug_data["Stderr"] = result.stderr.strip()[:100]
        else:
            if result.denial_reason:
                debug_data["Denial Reason"] = result.denial_reason
            if result.stderr:
                debug_data["Error"] = result.stderr.strip()[:200]
            if result.gatekeeper_response:
                debug_data["Gatekeeper"] = f"{result.gatekeeper_response.decision.value}: {result.gatekeeper_response.explanation}"
        
        for key, value in debug_data.items():
            print(f"{key:20s}: {value}")
        
        print("="*60 + "\n")

    async def _run_command(self, command: str) -> ExecutionResult:
        """
        Robust low-level execution with timeouts and output limits.
        """
        try:
            # Start process
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Read output with limits
            try:
                # We need to read potentially large streams without loading everything into memory
                # if it exceeds limits.
                stdout_data, stderr_data = await asyncio.wait_for(
                    self._read_streams(process), 
                    timeout=self.config.default_timeout_seconds
                )
                
                # Check exit code
                await process.wait() # Should return immediately as streams are closed
                
                return ExecutionResult(
                    success=(process.returncode == 0),
                    stdout=stdout_data,
                    stderr=stderr_data
                )
                
            except asyncio.TimeoutError:
                # Try graceful termination first
                process.terminate()
                try:
                    # Wait briefly for graceful shutdown
                    await asyncio.wait_for(process.wait(), timeout=2.0)
                except asyncio.TimeoutError:
                    # Force kill if doesn't terminate
                    process.kill()
                    await process.wait()
                
                logger.error("exec_timeout", command=command, timeout=self.config.default_timeout_seconds)
                return ExecutionResult(
                    success=False,
                    denial_reason=f"Command exceeded timeout of {self.config.default_timeout_seconds}s",
                    stderr=f"⏱️  Execution timed out after {self.config.default_timeout_seconds} seconds.\n"
                           f"Command was terminated to prevent hanging."
                )
                
        except Exception as e:
            logger.error("exec_failed", error=str(e))
            return ExecutionResult(
                success=False,
                stderr=f"System Execution Error: {str(e)}"
            )

    async def _read_streams(self, process) -> tuple[str, str]:
        """
        Read stdout/stderr up to max_output_bytes.
        """
        max_bytes = self.config.max_output_bytes
        
        async def read_stream_limited(stream):
            data = bytearray()
            while True:
                chunk = await stream.read(4096)
                if not chunk:
                    break
                data.extend(chunk)
                if len(data) > max_bytes:
                    data = data[:max_bytes] + b"\n... [TRUNCATED]"
                    # We continue consuming stream to not block process, but discard data?
                    # Or we just kill process? Standard shell behavior is usually to broken pipe if consumer stops.
                    # But here we are the consumer.
                    # To be safe, we stop reading. But if process keeps writing, it might block.
                    # Best practice: consume and discard remaining to let process exit gracefully-ish
                    # OR just return truncated and let process die when it tries to write to closed pipe (eventually)
                    break
            return data.decode('utf-8', errors='replace')

        # Run concurrent reads
        stdout_task = asyncio.create_task(read_stream_limited(process.stdout))
        stderr_task = asyncio.create_task(read_stream_limited(process.stderr))
        
        return await asyncio.gather(stdout_task, stderr_task)

    def _create_blocked_result(self, cmd: str, reason_short: str, reason_long: str, tier: RiskTier) -> ExecutionResult:
        return ExecutionResult(
            success=False,
            denial_reason=f"{reason_short}: {reason_long}",
            risk_tier=tier,
            stderr=f"SecureShell Blocked: {reason_long}"
        )

    async def _audit(self, cmd: str, reason: str, ctx: Dict, res: ExecutionResult):
        await self.audit_logger.log_execution(cmd, reason, ctx, res)
    
    async def shutdown(self):
        """Cleanup resources."""
        await self.audit_logger.stop()
