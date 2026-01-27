"""
SecureShell Quickstart - Full Cycle Demo
-----------------------------------------
Prerequisites:
    pip install -e .
    pip install openai
    export OPENAI_API_KEY=sk-...

This demo shows the complete cycle:
1. Agent tries to list files with `ls`
2. SecureShell blocks it (Windows uses `dir`)
3. Agent sees the error and corrects to `dir`
4. SecureShell allows and executes successfully
"""
import asyncio
import os
import platform
from openai import OpenAI as OpenAIClient

from secureshell import SecureShell
from secureshell.providers.openai import OpenAITools

MODEL = "gpt-4.1-mini"
MAX_ITERATIONS = 5  # Prevent infinite loops

async def main():
    if not os.getenv("OPENAI_API_KEY"):
        return print("❌ Please set OPENAI_API_KEY environment variable.")

    print(f"🚀 SecureShell Demo on {platform.system()} {platform.release()}\n")
    
    # Setup
    shell = SecureShell(os_info=f"{platform.system()} {platform.release()}")
    shell.config.debug_mode = True  # Show what's happening under the hood
    
    client = OpenAIClient()
    tools = [OpenAITools.get_tool_definition()]

    # Conversation starts
    messages = [
        {"role": "system", "content": "You are a helpful DevOps assistant with shell access. If a command fails, read the error and try again with the correct command for the OS."},
        {"role": "user", "content": "Please list all files in the current directory."}
    ]
    
    print(f"💬 User: {messages[-1]['content']}\n")

    # Agent loop - keep going until no more tool calls or max iterations
    for iteration in range(MAX_ITERATIONS):
        print(f"--- Iteration {iteration + 1} ---")
        
        response = client.chat.completions.create(
            model=MODEL, 
            messages=messages, 
            tools=tools
        )
        
        msg = response.choices[0].message
        messages.append(msg)

        # If agent wants to use tools
        if msg.tool_calls:
            print(f"🛠️  Agent is calling {len(msg.tool_calls)} tool(s)...\n")
            
            for tool_call in msg.tool_calls:
                # ONE LINE: Handle tool call
                tool_response = await shell.handle_tool_call(tool_call)
                messages.append(tool_response)
            
            # Continue loop to let agent react to results
            continue
        
        # If agent responds with text (no more tool calls)
        if msg.content:
            print(f"\n🤖 Agent: {msg.content}\n")
            break
    else:
        print("⚠️  Max iterations reached.")

    await shell.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
