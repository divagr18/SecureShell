"""
MCP Integration Example - OpenAI Agent using SecureShell MCP Server
--------------------------------------------------------------------
This demonstrates how an AI agent can use SecureShell via MCP.

Setup:
1. Start MCP server: python -m secureshell.integrations.mcp_server
2. Run this script: python examples/mcp_openai_example.py

The agent will connect to the MCP server and use execute_shell_command.
"""
import asyncio
import os
from openai import AsyncOpenAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Load .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


async def main():
    if not os.getenv("OPENAI_API_KEY"):
        return print("❌ Set OPENAI_API_KEY")
    
    print("🚀 OpenAI Agent + SecureShell MCP Demo\n")
    
    # Configure MCP server with debug mode
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "secureshell.integrations.mcp_server"],
        env={
            "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
            "SECURESHELL_MODEL": "gpt-4.1-mini",
            "SECURESHELL_DEBUG": "true"  # Enable debug mode
        }
    )
    
    # Start MCP server and create session
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize connection
            await session.initialize()
            
            # Get available tools from MCP server
            tools_result = await session.list_tools()
            print(f"📋 MCP Server tools: {[t.name for t in tools_result.tools]}\n")
            
            # Setup OpenAI client
            client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            
            # Convert MCP tools to OpenAI format
            openai_tools = [
                {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.inputSchema
                    }
                }
                for tool in tools_result.tools
            ]
            
            # Agent conversation
            messages = [
                {"role": "system", "content": "You are a helpful assistant. Use MCP tools to execute shell commands."},
                {"role": "user", "content": "List all Python files in the current directory"}
            ]
            
            print("💬 User: List all Python files in the current directory\n")
            
            # Agent loop
            for iteration in range(5):
                print(f"--- Iteration {iteration + 1} ---")
                
                response = await client.chat.completions.create(
                    model="gpt-4.1-mini",
                    messages=messages,
                    tools=openai_tools
                )
                
                message = response.choices[0].message
                messages.append(message)
                
                # Check for tool calls
                if message.tool_calls:
                    print(f"   Agent calling {len(message.tool_calls)} tool(s)...\n")
                    
                    for tool_call in message.tool_calls:
                        print(f"   Function: {tool_call.function.name}")
                        
                        # Execute via MCP
                        import json
                        args = json.loads(tool_call.function.arguments)
                        
                        print(f"   Arguments:")
                        print(f"     Command: {args.get('command', 'N/A')}")
                        print(f"     Reasoning: {args.get('reasoning', 'N/A')}")
                        
                        result = await session.call_tool(
                            name=tool_call.function.name,
                            arguments=args
                        )
                        
                        result_text = str(result.content[0].text) if result.content else ""
                        print(f"  Result:\n{result_text}\n")
                        
                        # Add result to messages
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": result_text
                        })
                    
                    continue
                
                # Final response
                if message.content:
                    print(f"\n🤖 Agent: {message.content}\n")
                    break
            else:
                print("⚠️  Max iterations reached")


if __name__ == "__main__":
    asyncio.run(main())
