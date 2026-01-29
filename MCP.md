# MCP Integration

SecureShell runs as an MCP server for Claude Desktop, Cline, and other MCP clients.

## Quick Start

### 1. Configure Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "secureshell": {
      "command": "python",
      "args": ["-m", "secureshell.integrations.mcp_server"],
      "env": {
        "OPENAI_API_KEY": "sk-..."
      }
    }
  }
}
```

See `mcp_config.json` for examples with all providers.

### 2. Restart Claude Desktop

The `execute_shell_command` tool will be available.

## Programmatic Usage

See `cookbook/mcp_example.py` for using the MCP server with your own OpenAI agent.

## Supported Providers

Auto-detects from environment:
- `OPENAI_API_KEY` → OpenAI
- `ANTHROPIC_API_KEY` → Anthropic
- `GEMINI_API_KEY` → Gemini
- `GROQ_API_KEY` → Groq
- `DEEPSEEK_API_KEY` → DeepSeek

## Security

All commands go through:
1. Risk classification
2. Sandbox validation
3. Gatekeeper LLM evaluation
4. Audit logging
