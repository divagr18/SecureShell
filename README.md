# SecureShell (Alpha)

A "sudo for LLMs" - drop-in shell execution wrapper that prevents hallucinated/destructive commands through AI-powered gatekeeping.

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


## Features

- **Risk Tiers**: Regex-based instantaneous classification (Green/Yellow/Red).
- **Gatekeeper LLM**: Uses a separate LLM call to evaluate intent and safety for risky commands.
- **Sandboxing**: Prevents directory traversal (`..`) and restricts access to allowed paths.
- **Audit Logging**: JSONL logs of every attempt, reasoning, and decision.
- **Industrial Stack**: Built with `pydantic`, `httpx`, `structlog`, and `tenacity`.

## Integrations

### OpenAI Function Calling
```python
from secureshell import SecureShell
from secureshell.providers.openai import OpenAITools

tools = [OpenAITools.get_tool_definition()]

# Pass 'tools' to your OpenAI client...
```

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

## Configuration

### Environment Variables
- `SECURESHELL_OPENAI_API_KEY` (or `OPENAI_API_KEY`)

### Customizing Rules
(Coming soon: yaml config support)
