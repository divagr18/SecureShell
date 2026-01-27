"""
Provider Demo - SecureShell with Different LLM Providers
---------------------------------------------------------
Shows how to use SecureShell with:
- OpenAI
- DeepSeek
- Anthropic Claude
- Google Gemini
- Groq (Llama)
- Ollama (Local)
- llama.cpp (Local)

Prerequisites:
    pip install -e .
    Set API keys in .env:
        OPENAI_API_KEY=sk-...
        DEEPSEEK_API_KEY=sk-...
        ANTHROPIC_API_KEY=sk-ant-...
        GEMINI_API_KEY=AIza...
        GROQ_API_KEY=gsk_...
"""
import asyncio
import os

from secureshell import SecureShell
from secureshell.providers import (
    OpenAIProvider,
    DeepSeekProvider,
    AnthropicProvider,
    GeminiProvider,
    GroqProvider,
    OllamaProvider,
    LlamaCppProvider
)


async def test_provider(name: str, provider, command: str = "echo 'Hello from SecureShell'"):
    """Test a single provider."""
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"{'='*60}")
    
    try:
        shell = SecureShell(provider=provider)
        shell.config.debug_mode = False  # Quiet mode for demo
        
        result = await shell.execute(
            command=command,
            reasoning="Testing provider integration"
        )
        
        if result.success:
            print(f"✅ {name}: ALLOWED")
            print(f"   Output: {result.stdout.strip()[:50]}")
        else:
            print(f"🛡️ {name}: BLOCKED")
            print(f"   Reason: {result.denial_reason}")
            
        await shell.shutdown()
        
    except Exception as e:
        print(f"❌ {name}: ERROR - {str(e)}")


async def main():
    print("🚀 SecureShell Provider Demo\n")
    
    # 1. OpenAI (GPT-4, GPT-3.5)
    if os.getenv("OPENAI_API_KEY"):
        await test_provider(
            "OpenAI (gpt-4.1-mini)",
            OpenAIProvider(
                api_key=os.getenv("OPENAI_API_KEY"),
                model="gpt-4.1-mini"
            )
        )
    
    # 2. DeepSeek
    if os.getenv("DEEPSEEK_API_KEY"):
        await test_provider(
            "DeepSeek",
            DeepSeekProvider(
                api_key=os.getenv("DEEPSEEK_API_KEY")
            )
        )
    
    # 3. Anthropic Claude
    if os.getenv("ANTHROPIC_API_KEY"):
        await test_provider(
            "Anthropic Claude",
            AnthropicProvider(
                api_key=os.getenv("ANTHROPIC_API_KEY"),
                model="claude-4-5-sonnet"
            )
        )
    
    # 4. Google Gemini
    if os.getenv("GEMINI_API_KEY"):
        await test_provider(
            "Google Gemini",
            GeminiProvider(
                api_key=os.getenv("GEMINI_API_KEY"),
                model="gemini-2.5-flash"
            )
        )
    
    # 5. Groq (Llama via API)
    if os.getenv("GROQ_API_KEY"):
        await test_provider(
            "Groq (Llama 3.1 70B)",
            GroqProvider(
                api_key=os.getenv("GROQ_API_KEY"),
                model="llama-3.1-70b-versatile"
            )
        )
    
    # 6. Ollama (Local)
    # Requires: ollama pull llama3.1:8b && ollama serve
    try:
        await test_provider(
            "Ollama (Local Llama)",
            OllamaProvider(model="llama3.1:8b")
        )
    except Exception:
        print("\n⚠️  Ollama not running (skipped)")
    
    # 7. llama.cpp (Local)
    # Requires: ./server -m model.gguf --api --port 8080
    try:
        await test_provider(
            "llama.cpp (Local)",
            LlamaCppProvider(base_url="http://localhost:8080/v1")
        )
    except Exception:
        print("\n⚠️  llama.cpp server not running (skipped)")
    
    print(f"\n{'='*60}")
    print("✅ Provider Demo Complete")
    print(f"{'='*60}")


if __name__ == "__main__":
    asyncio.run(main())
