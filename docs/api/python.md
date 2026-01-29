# Python API Reference

## SecureShell Class

The main entry point for the library.

```python
from secureshell import SecureShell

shell = SecureShell(
    provider=None,       # LLM Provider instance
    config=None,         # Config dict/object
    template=None,       # 'production', 'paranoid', etc.
    allowed_paths=None,  # List[str]
    blocked_paths=None   # List[str]
)
```

### Methods

#### `async execute(command: str, reasoning: str) -> ExecutionResult`
Executes a shell command with gatekeeper evaluation.

- **command**: The shell command to run
- **reasoning**: Context for why this command is needed
- **Returns**: `ExecutionResult`

#### `async shutdown()`
Cleans up resources. Always await this when done.

#### `get_os_info() -> str`
Returns the detected or configured OS string.

---

## LLM Providers

Constructors for supported LLM providers.

### `OpenAI`
```python
from secureshell.providers.openai import OpenAI

OpenAI(
    api_key: str,          # Required
    model: str = "gpt-4.1-mini",
    base_url: str = "https://api.openai.com/v1"
)
```

### `Anthropic`
```python
from secureshell.providers.anthropic import Anthropic

Anthropic(
    api_key: str,          # Required
    model: str = "claude-3-5-sonnet-20241022",
    base_url: str = "https://api.anthropic.com"
)
```

### `Ollama` (Local)
```python
from secureshell.providers.ollama import Ollama

Ollama(
    model: str = "llama3.1:8b",
    base_url: str = "http://localhost:11434"
)
```

### Others
- `Gemini(api_key, model)`
- `DeepSeek(api_key, model)`
- `Groq(api_key, model)`
- `LlamaCpp(base_url)`

---

## Tool Integrations

Helpers to create tools for other frameworks.

### LangChain
```python
from secureshell.integrations.langchain import create_secureshell_tool

# Returns a LangChain BaseTool compatible with agents
tool = create_secureshell_tool(shell)
```

### LangGraph
```python
from secureshell.integrations.langgraph import create_shell_node, ShellState

# Create a node function for your graph
shell_node = create_shell_node(shell)

# Or create a full workflow
workflow = create_shell_workflow(shell)
```

### MCP (Model Context Protocol)
```python
# Coming soon: Direct import for MCP Server class
# Currently supported via: python -m secureshell.integrations.mcp_server
```

---

## LLM Tool Constructors (Manual Integration)

Helpers to generate tool definitions for direct API use.

- `OpenAITools.get_tool_definition()`

---

## Configuration

### `SecureShellConfig`

Usually configured via `secureshell.yaml` or passed as `config={...}`.

```python
class SecureShellConfig:
    debug_mode: bool = False
    allowlist: List[str] = []
    blocklist: List[str] = []
    audit_log_path: str = "audit.jsonl"
```

---

## Models

### `ExecutionResult`

```python
@dataclass
class ExecutionResult:
    success: bool
    stdout: str
    stderr: str
    command: str
    risk_tier: RiskTier
    gatekeeper_reasoning: Optional[str]
```

### `RiskTier`

Enum with values:
- `GREEN`: Safe, read-only
- `YELLOW`: Needs review
- `RED`: Dangerous
- `BLOCKED`: Always denied
