"""
SecureShell with Anthropic Claude - Full Demo
----------------------------------------------
Prerequisites:
    export ANTHROPIC_API_KEY=sk-ant-...

Demonstrates complete agent cycle using Anthropic's tool use API.
"""
import asyncio
import os
import platform
from anthropic import Anthropic as AnthropicClient

from secureshell import SecureShell
from secureshell.providers.anthropic import Anthropic, AnthropicTools

MODEL = "claude-4-5-sonnet"
MAX_ITERATIONS = 5

async def main():
    if not os.getenv("ANTHROPIC_API_KEY"):
        return print("❌ Set ANTHROPIC_API_KEY")

    print(f"🚀 SecureShell + Claude on {platform.system()}\n")
    
    # Setup
    shell = SecureShell(
        provider=Anthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            model=MODEL
        ),
        os_info=f"{platform.system()} {platform.release()}"
    )
    shell.config.debug_mode = True
    
    client = AnthropicClient(api_key=os.getenv("ANTHROPIC_API_KEY"))
    tools = [AnthropicTools.get_tool_definition()]

    # Agent conversation
    messages = [
        {"role": "user", "content": "List all files in the current directory."}
    ]
    
    print(f"💬 User: {messages[0]['content']}\n")

    # Iteration loop
    for iteration in range(MAX_ITERATIONS):
        print(f"--- Iteration {iteration + 1} ---")
        
        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            messages=messages,
            tools=tools
        )
        
        messages.append({"role": "assistant", "content": response.content})

        # Check for tool use
        tool_use_blocks = [block for block in response.content if block.type == "tool_use"]
        
        if tool_use_blocks:
            print(f"🛠️  Claude calling {len(tool_use_blocks)} tool(s)...\n")
            
            tool_results = []
            for tool_use in tool_use_blocks:
                # Execute via SecureShell
                result = await shell.execute(
                    command=tool_use.input.get("command", ""),
                    reasoning=tool_use.input.get("reasoning", "")
                )
                
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_use.id,
                    "content": f"Success: {result.success}\\nOutput: {result.stdout if result.success else result.denial_reason}"
                })
            
            messages.append({"role": "user", "content": tool_results})
            continue
        
        # If no tool use, print response
        text_blocks = [block.text for block in response.content if hasattr(block, "text")]
        if text_blocks:
            print(f"\n🤖 Claude: {text_blocks[0]}\n")
            break
    else:
        print("⚠️  Max iterations reached.")

    await shell.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
