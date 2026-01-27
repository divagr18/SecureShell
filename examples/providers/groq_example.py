"""
SecureShell with Groq (Llama) - Full Demo
------------------------------------------
Prerequisites:
    export GROQ_API_KEY=gsk_...

Demonstrates complete agent cycle using Groq's fast inference.
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
from secureshell.providers.groq import Groq
from secureshell.providers.openai import OpenAITools

MODEL = "llama-3.3-70b-versatile"
MAX_ITERATIONS = 5

async def main():
    if not os.getenv("GROQ_API_KEY"):
        return print("❌ Set GROQ_API_KEY")

    print(f"🚀 SecureShell + Groq ({MODEL}) on {platform.system()}\n")
    
    # Setup
    shell = SecureShell(
        provider=Groq(
            api_key=os.getenv("GROQ_API_KEY"),
            model=MODEL
        ),
        os_info=f"{platform.system()} {platform.release()}"
    )
    shell.config.debug_mode = True
    
    # Groq uses OpenAI-compatible API
    client = OpenAIClient(
        api_key=os.getenv("GROQ_API_KEY"),
        base_url="https://api.groq.com/openai/v1"
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
            print(f"🛠️  Agent calling {len(msg.tool_calls)} tool(s)...\n")
            
            for tool_call in msg.tool_calls:
                messages.append(await shell.handle_tool_call(tool_call))
            
            continue
        
        if msg.content:
            print(f"\n🤖 Agent: {msg.content}\n")
            break
    else:
        print("⚠️  Max iterations reached.")

    await shell.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
