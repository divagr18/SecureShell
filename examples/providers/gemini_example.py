"""
SecureShell with Google Gemini - Full Demo
-------------------------------------------
Prerequisites:
    export GOOGLE_API_KEY=AIza...
    or
    export GEMINI_API_KEY=AIza...

Demonstrates complete agent cycle using Gemini function calling.
Follows official Gemini function calling pattern from docs.
"""
import asyncio
import os
import platform
from google import genai
from google.genai import types

# Load .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from secureshell import SecureShell
from secureshell.providers.gemini import Gemini, GeminiTools

MODEL = "gemini-2.5-flash"
MAX_ITERATIONS = 5

async def main():
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        return print("❌ Set GOOGLE_API_KEY or GEMINI_API_KEY")

    print(f"🚀 SecureShell + Gemini on {platform.system()}\n")
    
    # Setup SecureShell
    shell = SecureShell(
        provider=Gemini(
            api_key=api_key,
            model=MODEL
        ),
        os_info=f"{platform.system()} {platform.release()}"
    )
    shell.config.debug_mode = True
    
    # Setup Gemini client
    client = genai.Client(api_key=api_key)
    
    # Configure tools
    tools = types.Tool(function_declarations=[GeminiTools.get_tool_definition()])
    config = types.GenerateContentConfig(tools=[tools])
    
    # Initialize conversation with user message
    user_message = "List all files in the current directory."
    print(f"💬 User: {user_message}\n")
    
    contents = [
        types.Content(
            role="user",
            parts=[types.Part(text=user_message)]
        )
    ]
    
    # Iteration loop
    for iteration in range(MAX_ITERATIONS):
        print(f"--- Iteration {iteration + 1} ---")
        
        response = client.models.generate_content(
            model=MODEL,
            contents=contents,
            config=config
        )

        # Check for function calls
        part = response.candidates[0].content.parts[0]
        
        if hasattr(part, 'function_call') and part.function_call:
            fc = part.function_call
            print(f"🛠️  Gemini calling function: {fc.name}\n")
            
            # Execute via SecureShell
            result = await shell.execute(
                command=fc.args.get("command", ""),
                reasoning=fc.args.get("reasoning", "")
            )
            
            # Create function response part
            function_response_part = types.Part.from_function_response(
                name=fc.name,
                response={
                    "result": {
                        "success": result.success,
                        "output": result.stdout if result.success else result.stderr
                    }
                }
            )
            
            # Append model's response (with function call) to contents
            contents.append(response.candidates[0].content)
            
            # Append function response as new user turn
            contents.append(
                types.Content(role="user", parts=[function_response_part])
            )
            
            continue
        
        # If no function call, print final response
        if response.text:
            print(f"\n🤖 Gemini: {response.text}\n")
            break
    else:
        print("⚠️  Max iterations reached.")

    await shell.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
