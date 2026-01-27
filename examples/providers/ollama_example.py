"""
SecureShell with Ollama (Local) - Full Demo
--------------------------------------------
Prerequisites:
    1. Install Ollama: https://ollama.ai
    2. Pull a model: ollama pull llama3.1:8b
    3. Start server: ollama serve

Demonstrates complete agent cycle using Ollama's OpenAI-compatible API.
"""
import asyncio
import platform
from openai import OpenAI as OpenAIClient

from secureshell import SecureShell
from secureshell.providers.ollama import Ollama
from secureshell.providers.openai import OpenAITools  # Ollama uses OpenAI-compatible tools

MODEL = "llama3.1:8b"
OLLAMA_BASE_URL = "http://localhost:11434/v1"
MAX_ITERATIONS = 5

async def main():
    print(f"🚀 SecureShell + Ollama ({MODEL}) on {platform.system()}\n")
    
    # Setup SecureShell
    shell = SecureShell(
        provider=Ollama(
            model=MODEL,
            base_url="http://localhost:11434"
        ),
        os_info=f"{platform.system()} {platform.release()}"
    )
    shell.config.debug_mode = True
    
    # Setup Ollama client (OpenAI-compatible)
    client = OpenAIClient(
        base_url=OLLAMA_BASE_URL,
        api_key="ollama"  # Ollama doesn't need a real API key
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
        
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                tools=tools
            )
        except Exception as e:
            print(f"❌ Error: {e}")
            print("Make sure Ollama is running: ollama serve")
            break
        
        msg = response.choices[0].message
        messages.append(msg)

        if msg.tool_calls:
            print(f"🛠️  Ollama calling {len(msg.tool_calls)} tool(s)...\n")
            
            for tool_call in msg.tool_calls:
                messages.append(await shell.handle_tool_call(tool_call))
            
            continue
        
        if msg.content:
            print(f"\n🤖 Ollama: {msg.content}\n")
            break
    else:
        print("⚠️  Max iterations reached.")

    await shell.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
