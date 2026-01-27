# Provider Examples

This directory contains quickstart examples for each LLM provider supported by SecureShell.

## Available Providers

### Cloud-Based

- **[openai_example.py](openai_example.py)** - OpenAI GPT models
  - Requires: `OPENAI_API_KEY`
  - Models: gpt-4.1, gpt-4.1-mini, gpt-5

- **[anthropic_example.py](anthropic_example.py)** - Anthropic Claude
  - Requires: `ANTHROPIC_API_KEY`
  - Models: claude-sonnet-4-5, claude-haiku-4-5

- **[gemini_example.py](gemini_example.py)** - Google Gemini
  - Requires: `GEMINI_API_KEY`
  - Models: gemini-2.5-flash, gemini-2.5-flash-lite

### Local Models

- **[ollama_example.py](ollama_example.py)** - Ollama (easiest local setup)
  - Requires: Ollama running (`ollama serve`)
  - Models: llama3.1, mistral, codellama, etc.

- **llama_cpp_example.py** - llama.cpp server
  - Requires: llama.cpp server running
  - For advanced users wanting maximum control

## Usage

1. Install SecureShell:
   ```bash
   pip install -e .
   ```

2. Set up API key (for cloud providers):
   ```bash
   export OPENAI_API_KEY=sk-...
   # or
   export ANTHROPIC_API_KEY=sk-ant-...
   # or
   export GEMINI_API_KEY=AIza...
   ```

3. Run an example:
   ```bash
   python examples/providers/openai_example.py
   ```

## Import Pattern

All providers follow the same pattern:

```python
from secureshell import SecureShell
from secureshell.providers.openai import OpenAI, OpenAITools

# Initialize provider
provider = OpenAI(api_key="...", model="gpt-4.1-mini")

# Use with SecureShell
shell = SecureShell(provider=provider)
```

## Notes

- OpenAI, DeepSeek, Groq, and llama.cpp use the same `OpenAITools` for tool definitions (OpenAI-compatible API)
- Anthropic, Gemini, and Ollama have their own API formats and don't need separate tool classes
- For full agent integration, see [../quickstart.py](../quickstart.py)
