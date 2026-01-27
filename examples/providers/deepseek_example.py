"""
SecureShell with DeepSeek - Full Demo
--------------------------------------
Prerequisites:
    export DEEPSEEK_API_KEY=sk-...

DeepSeek uses OpenAI-compatible API for fast, affordable inference.
"""
import asyncio
import os
import platform
from openai import OpenAI as OpenAIClient

# Load .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from secureshell import SecureShell
from secureshell.providers.deepseek import DeepSeek
from secureshell.providers.openai import OpenAITools

MODEL = "deepseek-chat"
MAX_ITERATIONS = 5

async def main():
    if not os.getenv("DEEPSEEK_API_KEY"):
        return print("❌ Set DEEPSEEK_API_KEY")

    print(f"🚀 SecureShell + DeepSeek on {platform.system()}\n")
    
    # Setup SecureShell
    shell = SecureShell(
        provider=DeepSeek(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            model=MODEL
        ),
        os_info=f"{platform.system()} {platform.release()}"
    )
    shell.config.debug_mode = True
    
    # DeepSeek uses OpenAI-compatible API
    client = OpenAIClient(
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        base_url="https://api.deepseek.com"
    )
    tools = [OpenAITools.get_tool_definition()]

    # Agent conversation
    messages = [
        {"role": "system", "content": "You are a helpful assistant. If a command fails, adapt to the OS."},
        {"role": "user", "content": "List all files in the current directory."}
    ]
    
    print(f"💬 User: {messages[-1]['content']}\n")

    # Iteration loop
    for iteration in range(MAX_ITERATIONS):
        print(f"--- Iteration {iteration + 1} ---")
        
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=tools
        )
        
        msg = response.choices[0].message
        messages.append(msg)

        if msg.tool_calls:
            print(f"🛠️  DeepSeek calling {len(msg.tool_calls)} tool(s)...\n")
            
            for tool_call in msg.tool_calls:
                messages.append(await shell.handle_tool_call(tool_call))
            
            continue
        
        if msg.content:
            print(f"\n🤖 DeepSeek: {msg.content}\n")
            break
    else:
        print("⚠️  Max iterations reached.")

    await shell.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
