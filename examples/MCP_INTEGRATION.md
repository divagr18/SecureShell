# SecureShell MCP Integration

SecureShell can be used as an MCP (Model Context Protocol) server, making it available to Claude Desktop, Cline, and other MCP clients.

## Quick Start

### 1. Install Dependencies

```bash
pip install mcp
```

### 2. Configure Claude Desktop

Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json` on Mac):

```json
{
  "mcpServers": {
    "secureshell": {
      "command": "python",
      "args": ["-m", "secureshell.integrations.mcp_server"],
      "env": {
        "OPENAI_API_KEY": "your-key-here",
        "SECURESHELL_MODEL": "gpt-4.1-mini"
      }
    }
  }
}
```

### 3. Restart Claude Desktop

The `execute_shell_command` tool will now be available!

## Usage Example

In Claude Desktop, you can ask:

> "List all Python files in the current directory"

Claude will use the `execute_shell_command` tool:
- **Command**: `find . -name "*.py"`
- **Reasoning**: "User wants to see all Python files"

SecureShell's gatekeeper will evaluate safety and execute if approved.

## Features

✅ **AI Gatekeeper** - OpenAI evaluates command safety  
✅ **Sandboxed** - Path restrictions prevent escapes  
✅ **Audited** - All commands logged to `secureshell_audit.jsonl`  
✅ **Rich Responses** - Formatted output with success/failure indicators

## Environment Variables

- `OPENAI_API_KEY` - Required for gatekeeper
- `SECURESHELL_MODEL` - Model to use (default: gpt-4o-mini)
- `ANTHROPIC_API_KEY` - If using Anthropic provider
- `GEMINI_API_KEY` - If using Gemini provider

## Testing Locally

```bash
# Run the MCP server directly (stdio mode)
python -m secureshell.integrations.mcp_server

# It will wait for JSON-RPC messages on stdin
```

## Architecture

```
┌─────────────────┐
│  Claude Desktop │
│   (MCP Client)  │
└────────┬────────┘
         │ JSON-RPC over stdio
         ▼
┌─────────────────┐
│  MCP Server     │
│  (SecureShell)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Gatekeeper LLM │
│  Risk Classifier│
│  Sandbox        │
│  Audit Logger   │
└─────────────────┘
```

## Security

Commands go through multiple layers:
1. **Risk Classification** - Pattern matching for dangerous commands
2. **Sandbox Validation** - Path canonicalization and whitelisting
3. **Gatekeeper LLM** - AI evaluation of command + reasoning
4. **Audit Logging** - All executions logged for review

## Limitations

- Requires API key for gatekeeper
- Adds ~1-2s latency for LLM evaluation
- Commands timeout after 30s (configurable)
