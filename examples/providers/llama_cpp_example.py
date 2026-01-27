"""
SecureShell with llama.cpp Server - Full Demo
----------------------------------------------
Prerequisites:
    1. Build llama.cpp: https://github.com/ggerganov/llama.cpp
    2. Download a model (e.g., llama-3.1-8b-instruct.gguf)
    3. Start server: ./llama-server -m model.gguf --port 8080

Demonstrates complete agent cycle using llama.cpp OpenAI-compatible server.
"""
import asyncio
import platform
from openai import OpenAI as OpenAIClient

from secureshell import SecureShell
from secureshell.providers.llama_cpp import LlamaCpp
from secureshell.providers.openai import OpenAITools

MODEL = "llama-3.1-8b-instruct"  # Model name (doesn't matter for llama.cpp)
LLAMA_CPP_URL = "http://localhost:8080/v1"
MAX_ITERATIONS = 5

async def main():
    print(f"🚀 SecureShell + llama.cpp on {platform.system()}\n")
    
    # Setup SecureShell
    shell = SecureShell(
        provider=LlamaCpp(
            base_url="http://localhost:8080",
            model=MODEL
        ),
        os_info=f"{platform.system()} {platform.release()}"
    )
    shell.config.debug_mode = True
    
    # llama.cpp uses OpenAI-compatible API
    client = OpenAIClient(
        base_url=LLAMA_CPP_URL,
        api_key="not-needed"  # llama.cpp doesn't require API key
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
            print("Make sure llama.cpp server is running: ./llama-server -m model.gguf")
            break
        
        msg = response.choices[0].message
        messages.append(msg)

        if msg.tool_calls:
            print(f"🛠️  llama.cpp calling {len(msg.tool_calls)} tool(s)...\n")
            
            for tool_call in msg.tool_calls:
                messages.append(await shell.handle_tool_call(tool_call))
            
            continue
        
        if msg.content:
            print(f"\n🤖 llama.cpp: {msg.content}\n")
            break
    else:
        print("⚠️  Max iterations reached.")

    await shell.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
