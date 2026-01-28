"""
LangChain Integration for SecureShell
--------------------------------------
Provides a custom LangChain tool for secure shell command execution.
"""
from typing import Optional, Type
from pydantic import BaseModel, Field
from langchain.tools import BaseTool

from secureshell import SecureShell
from secureshell.models import ExecutionResult


class ShellCommandInput(BaseModel):
    """Input schema for shell command execution."""
    command: str = Field(description="The shell command to execute")
    reasoning: str = Field(description="Explanation of why this command is needed")


class SecureShellTool(BaseTool):
    """LangChain tool for secure shell command execution."""
    
    name: str = "execute_shell_command"
    description: str = (
        "Execute shell commands securely with AI gatekeeper validation. "
        "Gatekeeper may ALLOW, DENY, or CHALLENGE (request clarification for vague reasoning). "
        "Commands are sandboxed and audited. Use this for file operations, "
        "system commands, git operations, and other shell tasks."
    )
    args_schema: Type[BaseModel] = ShellCommandInput
    
    # SecureShell instance (must be set before use)
    shell: Optional[SecureShell] = None
    
    def _run(self, command: str, reasoning: str) -> str:
        """Execute the command synchronously."""
        if not self.shell:
            return "Error: SecureShell instance not configured"
        
        # LangChain tools expect sync, but SecureShell is async
        # We need to run it in an event loop
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(
            self.shell.execute(command=command, reasoning=reasoning)
        )
        
        return self._format_result(result)
    
    async def _arun(self, command: str, reasoning: str) -> str:
        """Execute the command asynchronously."""
        if not self.shell:
            return "Error: SecureShell instance not configured"
        
        result = await self.shell.execute(command=command, reasoning=reasoning)
        return self._format_result(result)
    
    def _format_result(self, result: ExecutionResult) -> str:
        """Format execution result for LangChain."""
        if result.success:
            return f"[SUCCESS]\n{result.stdout}"
        else:
            output = f"[BLOCKED] {result.denial_reason or 'Execution failed'}"
            if result.stderr:
                output += f"\nError: {result.stderr}"
            if result.gatekeeper_response:
                output += f"\nGatekeeper: {result.gatekeeper_response.decision.value}"
                output += f"\n{result.gatekeeper_response.explanation}"
            return output


def create_secureshell_tool(shell: SecureShell) -> SecureShellTool:
    """
    Create a LangChain tool from a SecureShell instance.
    
    Args:
        shell: Configured SecureShell instance
        
    Returns:
        LangChain tool ready to use with agents
        
    Example:
        >>> from secureshell import SecureShell
        >>> from secureshell.providers.openai import OpenAI
        >>> from secureshell.integrations.langchain import create_secureshell_tool
        >>> 
        >>> shell = SecureShell(provider=OpenAI(api_key="..."))
        >>> tool = create_secureshell_tool(shell)
        >>> 
        >>> # Use with LangChain agent
        >>> from langchain.agents import initialize_agent, AgentType
        >>> agent = initialize_agent([tool], llm, agent=AgentType.OPENAI_FUNCTIONS)
    """
    tool = SecureShellTool()
    tool.shell = shell
    return tool
