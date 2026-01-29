# SecureShell (Alpha)

A "sudo for LLMs" - drop-in shell execution wrapper that prevents hallucinated/destructive commands through AI-powered gatekeeping.

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Security Templates](#security-templates)
- [Features](#features)
- [Configuration](#configuration)
  - [YAML Configuration](#yaml-configuration)
  - [Environment Variables](#environment-variables)
- [Challenge Mode](#challenge-mode)
- [Providers](#providers)
- [Integrations](#integrations)
- [Customizing Rules](#customizing-rules)

## Installation

```bash
pip install secureshell
```

## Quick Start

See [examples/quickstart.py](examples/quickstart.py) for a complete, production-ready example using OpenAI.

```bash
# 1. Set your API Key
export OPENAI_API_KEY=sk-...

# 2. Run the Quickstart Agent
python examples/quickstart.py
```

### What happens?
1. The Agent asks to list files (or whatever you prompt it to do).
2. SecureShell intercepts the command.
3. **Green Tier** commands (like `ls`, `dir`) run immediately.
4. **Yellow/Red Tier** commands (like `rm`, `git push`) trigger the Gatekeeper LLM.
5. The command runs (or is blocked) and output is returned to the Agent.

## Security Templates

**No YAML configuration required!** Use pre-built security templates for common use cases:

```python
from secureshell import SecureShell

# Choose a template that fits your use case
shell = SecureShell(template="paranoid")     # 🔒 Maximum security
shell = SecureShell(template="development")  # 🛠️  Local dev friendly
shell = SecureShell(template="production")   # 🏭 Production safe
shell = SecureShell(template="ci_cd")        # 🚀 CI/CD optimized
```

### Template Quick Reference

| Template | Best For | Allowlist Highlights | Blocklist Highlights |
|----------|----------|---------------------|---------------------|
| 🔒 **paranoid** | Untrusted agents | `ls`, `pwd`, `echo`, `cat` | `rm`, `dd`, `chmod`, `sudo`, `curl`, `wget` |
| 🛠️ **development** | Local development | `git`, `npm`, `pip`, `node`, `python` | `dd`, `mkfs`, `sudo` |
| 🏭 **production** | Production systems | `ls`, `pwd`, `echo`, `cat` | `rm`, `dd`, `chmod`, `sudo`, `mkfs` |
| 🚀 **ci_cd** | CI/CD pipelines | `git`, `npm`, `pip`, `docker`, `node` | `dd`, `mkfs`, `sudo` |

📖 **Full documentation:** [examples/SECURITY_TEMPLATES.md](examples/SECURITY_TEMPLATES.md)  
🎯 **Try it:** Run `python examples/templates_demo.py` to see all templates in action.


## Features

- **Risk Tiers**: Regex-based instantaneous classification (Green/Yellow/Red).
- **Gatekeeper LLM**: Uses a separate LLM call to evaluate intent and safety for risky commands.
- **Challenge Mode**: Gatekeeper can request clarification for ambiguous commands (ALLOW/DENY/CHALLENGE).
- **Security Templates**: Pre-built configurations for common use cases (paranoid, development, production, ci_cd).
- **YAML Configuration**: Customize allowlist/blocklist rules via `secureshell.yaml`.
- **Multi-Provider Support**: OpenAI, Anthropic, Gemini, DeepSeek, Groq, Ollama, llama.cpp.
- **Framework Integrations**: OpenAI tools, LangChain, LangGraph, and Anthropic MCP.
- **Sandboxing**: Prevents directory traversal (`..`) and restricts access to allowed paths.
- **Audit Logging**: JSONL logs of every attempt, reasoning, and decision.


For detailed configuration and usage, see the sections below.

## Configuration

### YAML Configuration

SecureShell supports YAML-based configuration via a `secureshell.yaml` file in your working directory. This allows you to customize allowlist and blocklist rules without modifying code.

#### Example Configuration

```yaml
allowlist:
  - "echo"
  - "ls"

blocklist:
  - "rm"
  - "dd"
```

See [examples/config_test.py](examples/config_test.py) for a demonstration.

#### How It Works

1. **Allowlist**: Command types (first word) matching these patterns bypass ALL security checks (including risk tiers and gatekeeper). Use with extreme caution!
2. **Blocklist**: Command types matching these patterns are immediately blocked, regardless of risk tier or reasoning.
3. **Pattern Matching**: Extracts the command type (first word) and matches exactly. For example, `"rm"` in the blocklist will block `rm file.txt`, `rm -rf /`, etc.

### Environment Variables

SecureShell can be configured via environment variables with the `SECURESHELL_` prefix:

- `SECURESHELL_OPENAI_API_KEY` (or `OPENAI_API_KEY`) - API key for OpenAI provider
- `SECURESHELL_ANTHROPIC_API_KEY` (or `ANTHROPIC_API_KEY`) - API key for Anthropic provider
- `SECURESHELL_GEMINI_API_KEY` (or `GEMINI_API_KEY`) - API key for Google Gemini
- `SECURESHELL_DEBUG_MODE` - Enable verbose debugging output (true/false)
- `SECURESHELL_PROVIDER` - Default provider to use (openai, anthropic, gemini, ollama, etc.)

**Programmatic Configuration:**

You can also configure OS information programmatically:

```python
shell = SecureShell(
    template="production",
    os_info="Windows  11 Enterprise"  # Tell the gatekeeper what OS you're on
)
```

The `os_info` parameter helps the LLM gatekeeper make OS-specific decisions (e.g., knowing that `dir` is Windows equivalent of `ls`).

See [secureshell/config.py](secureshell/config.py) for all available options.

## Challenge Mode

SecureShell's gatekeeper can return three decision types:
- **ALLOW** - Command is safe and will be executed
- **DENY** - Command is rejected due to safety concerns
- **CHALLENGE** - Gatekeeper needs more information or clarification

### When CHALLENGE is Returned

The gatekeeper returns `CHALLENGE` when:
- Reasoning provided is vague or unclear
- Intent is ambiguous or missing context
- More information is needed to make a safe decision
- The scope of the command is uncertain

### Example

See [examples/challenge_demo.py](examples/challenge_demo.py) for a full demonstration.

## Providers

SecureShell supports multiple LLM providers for the gatekeeper. All providers implement the same interface, making it easy to switch between them.

### Supported Providers

#### Cloud-Based
- **OpenAI** - GPT-4.1, GPT-4.1-mini, GPT-5.2
- **Anthropic** - Claude Sonnet 4.5, Claude Haiku 4.5
- **Google Gemini** - Gemini 2.5 Flash, Gemini 2.5 Flash Lite
- **DeepSeek** - DeepSeek models (OpenAI-compatible)
- **Groq** - Fast inference (OpenAI-compatible)

#### Local Models
- **Ollama** - Easiest local setup (llama3.1, mistral, codellama, etc.)
- **llama.cpp** - Maximum control for advanced users

### Quick Provider Examples

```python
# OpenAI
from secureshell.providers.openai import OpenAI
provider = OpenAI(api_key="sk-...", model="gpt-4.1-mini")

# Anthropic
from secureshell.providers.anthropic import Anthropic
provider = Anthropic(api_key="sk-ant-...", model="claude-sonnet-4-5")

# Google Gemini
from secureshell.providers.gemini import Gemini
provider = Gemini(api_key="AIza...", model="gemini-2.5-flash")

# Ollama (local)
from secureshell.providers.ollama import Ollama
provider = Ollama(model="llama3.1", base_url="http://localhost:11434")

# llama.cpp (local)
from secureshell.providers.llama_cpp import LlamaCpp
provider = LlamaCpp(model="llama-3.1-8b", base_url="http://localhost:8080")

# Use with SecureShell
shell = SecureShell(provider=provider)
```

For detailed provider examples, see [examples/providers/](examples/providers/).

## Integrations

SecureShell integrates with popular LLM frameworks and tools:

### OpenAI Function Calling

```python
from secureshell import SecureShell
from secureshell.providers.openai import OpenAITools

tools = [OpenAITools.get_tool_definition()]

# Pass 'tools' to your OpenAI client...
```

### LangChain

```python
from secureshell import SecureShell
from secureshell.integrations.langchain import SecureShellTool

# Create tool
shell_tool = SecureShellTool(provider=...)

# Use with LangChain agents
```

See [examples/langchain_example.py](examples/langchain_example.py) for details.

### LangGraph

SecureShell works seamlessly with LangGraph for multi-agent workflows.

See [examples/langgraph_example.py](examples/langgraph_example.py) for a complete example.

### Anthropic MCP (Claude Desktop)

To use SecureShell with Claude Desktop:

1. Install with MCP extras:
   ```bash
   pip install secureshell[anthropic]
   ```
2. Configure `claude_desktop_config.json`:
   ```json
   {
     "mcpServers": {
       "secureshell": {
         "command": "python",
         "args": ["-m", "secureshell.integrations.mcp"]
       }
     }
   }
   ```

See [MCP.md](MCP.md) for detailed setup instructions.

## Customizing Rules

### Risk Tiers

Commands are automatically classified into risk tiers:
- **GREEN**: Auto-allow (ls, pwd, echo)
- **YELLOW**: Gatekeeper review (rm, git push)
- **RED**: Strict review (rm -rf, sudo)
- **BLOCKED**: Always deny (dd, mkfs, fork bombs)
