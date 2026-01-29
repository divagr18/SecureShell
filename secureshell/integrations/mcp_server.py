"""
SecureShell MCP Server
----------------------
Exposes SecureShell's execute_shell_command as an MCP (Model Context Protocol) tool.
Compatible with Claude Desktop, Cline, and other MCP clients.

Usage:
    python -m secureshell.integrations.mcp_server

Configuration for Claude Desktop:
    See cookbook/mcp_config.json
"""
import asyncio
import sys
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp import types

from secureshell import SecureShell
from secureshell.providers.openai import OpenAI


# Global SecureShell instance
shell: SecureShell = None


async def main():
    """Run the MCP server."""
    global shell
    
    # Auto-detect provider from environment variables
    import os
    
    provider = None
    provider_name = os.getenv("SECURESHELL_PROVIDER", "").lower()
    
    # If SECURESHELL_PROVIDER is set, use that
    if provider_name == "openai" or (not provider_name and os.getenv("OPENAI_API_KEY")):
        from secureshell.providers.openai import OpenAI
        provider = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY", ""),
            model=os.getenv("SECURESHELL_MODEL", "gpt-4.1-mini")
        )
    elif provider_name == "anthropic" or (not provider_name and os.getenv("ANTHROPIC_API_KEY")):
        from secureshell.providers.anthropic import Anthropic
        provider = Anthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY", ""),
            model=os.getenv("SECURESHELL_MODEL", "claude-sonnet-4-5")
        )
    elif provider_name == "gemini" or (not provider_name and os.getenv("GEMINI_API_KEY")):
        from secureshell.providers.gemini import Gemini
        provider = Gemini(
            api_key=os.getenv("GEMINI_API_KEY", ""),
            model=os.getenv("SECURESHELL_MODEL", "gemini-2.5-flash")
        )
    elif provider_name == "groq" or (not provider_name and os.getenv("GROQ_API_KEY")):
        from secureshell.providers.groq import Groq
        provider = Groq(
            api_key=os.getenv("GROQ_API_KEY", ""),
            model=os.getenv("SECURESHELL_MODEL", "llama-3.3-70b-versatile")
        )
    elif provider_name == "deepseek" or (not provider_name and os.getenv("DEEPSEEK_API_KEY")):
        from secureshell.providers.deepseek import DeepSeek
        provider = DeepSeek(
            api_key=os.getenv("DEEPSEEK_API_KEY", ""),
            model=os.getenv("SECURESHELL_MODEL", "deepseek-chat")
        )
    else:
        # Fallback to OpenAI with empty key (will fail but with clear error)
        from secureshell.providers.openai import OpenAI
        provider = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY", ""),
            model=os.getenv("SECURESHELL_MODEL", "gpt-4.1-mini")
        )
    
    shell = SecureShell(provider=provider)
    
    # Enable debug mode if requested
    if os.getenv("SECURESHELL_DEBUG", "").lower() in ("true", "1", "yes"):
        shell.config.debug_mode = True
    
    # Create MCP server
    server = Server("secureshell")
    
    @server.list_tools()
    async def handle_list_tools() -> list[types.Tool]:
        """List available tools."""
        return [
            types.Tool(
                name="execute_shell_command",
                description=(
                    "Execute shell commands securely with AI gatekeeper validation. "
                    "Gatekeeper may ALLOW, DENY, or CHALLENGE (request clarification). "
                    "Commands are sandboxed and audited. Use this for file operations, "
                    "system commands, git operations, and other shell tasks."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "The shell command to execute (e.g., 'ls -la', 'git status')"
                        },
                        "reasoning": {
                            "type": "string",
                            "description": "Explain why this command is needed and what it will accomplish"
                        }
                    },
                    "required": ["command", "reasoning"]
                }
            )
        ]
    
    @server.call_tool()
    async def handle_call_tool(
        name: str,
        arguments: dict | None
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        """Handle tool execution."""
        if name != "execute_shell_command":
            raise ValueError(f"Unknown tool: {name}")
        
        if not arguments:
            raise ValueError("Missing arguments")
        
        command = arguments.get("command", "")
        reasoning = arguments.get("reasoning", "")
        
        if not command:
            raise ValueError("Missing required argument: command")
        
        # Execute via SecureShell
        result = await shell.execute(command=command, reasoning=reasoning)
        
        # Format response
        if result.success:
            response_text = f"[SUCCESS] Command executed successfully\n\n**Output:**\n```\n{result.stdout}\n```"
            if result.stderr:
                response_text += f"\n\n**Stderr:**\n```\n{result.stderr}\n```"
        else:
            response_text = f"[BLOCKED] Command blocked or failed\n\n**Reason:** {result.denial_reason or 'Execution failed'}"
            if result.stderr:
                response_text += f"\n\n**Error:**\n```\n{result.stderr}\n```"
            if result.gatekeeper_response:
                response_text += f"\n\n**Gatekeeper:** {result.gatekeeper_response.decision.value}"
                response_text += f"\n{result.gatekeeper_response.explanation}"
        
        return [types.TextContent(type="text", text=response_text)]
    
    # Run server
    async with stdio_server() as (read_stream, write_stream):
        init_options = InitializationOptions(
            server_name="secureshell",
            server_version="1.0.0",
            capabilities=server.get_capabilities(
                notification_options=NotificationOptions(),
                experimental_capabilities={}
            )
        )
        
        await server.run(
            read_stream,
            write_stream,
            init_options
        )
    
    # Cleanup
    await shell.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
