# Model Context Protocol (MCP) Integration

SecureShell provides first-class support for the [Model Context Protocol](https://modelcontextprotocol.io/), allowing you to expose secure shell execution as an MCP tool for Claude Desktop and other AI applications.

## What is MCP?

Model Context Protocol (MCP) is a standard for connecting AI assistants to external tools and data sources. It enables Claude Desktop and other AI apps to safely interact with your local environment.

## Quick Setup

### 1. Install Dependencies

```bash
npm install @modelcontextprotocol/sdk
```

### 2. Run MCP Server

```bash
cd cookbook/secureshell-ts
npx tsx mcp_server.ts
```

See the complete implementation in [`cookbook/secureshell-ts/mcp_server.ts`](../cookbook/secureshell-ts/mcp_server.ts).

## Claude Desktop Integration

Add SecureShell to Claude Desktop's configuration:

**macOS/Linux:** `~/Library/Application Support/Claude/claude_desktop_config.json`

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "secureshell": {
      "command": "npx",
      "args": ["-y", "tsx", "/path/to/secureshell/cookbook/secureshell-ts/mcp_server.ts"],
      "env": {
        "OPENAI_API_KEY": "sk-..."
      }
    }
  }
}
```

## How It Works

The MCP tool exposes a single command:

**Tool:** `execute_shell_command`

**Inputs:**
- `command` - Shell command to execute
- `reasoning` - Why the command should run

**Output:** Command result or gatekeeper denial reason

## Example Interaction

```
User: "List files in my current directory"

Claude: [Calls execute_shell_command: "ls -la"]
SecureShell: [On Windows] DENY - Use 'dir' instead

Claude: [Calls execute_shell_command: "dir"]
SecureShell: ALLOW
[Returns directory listing]

Claude: "Here are your files: ..."
```

The gatekeeper helps Claude learn platform-specific commands.

## Security Configuration

When exposing shell execution via MCP, use strict security:

```typescript
const shell = new SecureShell({
    template: 'paranoid', // Maximum security
    config: { 
        debugMode: true, // Monitor all commands
        allowedPaths: ['/workspace'], // Restrict access
        blockedPaths: ['/etc', '/sys']
    }
});
```

## AI Agent Demo

Try the interactive demo that shows an AI agent calling the MCP server:

```bash
cd cookbook/secureshell-ts
npx tsx mcp_client_demo.ts
```

The agent will:
1. Connect to the MCP server
2. List available tools
3. Call `execute_shell_command` to list files and read package.json
4. Self-correct if commands are blocked

## Debugging

**Enable debug logging:**
```typescript
const shell = new SecureShell({ config: { debugMode: true } });
```

**Check Claude Desktop logs:**
- macOS: `~/Library/Logs/Claude/`
- Windows: `%APPDATA%\Claude\logs\`

**Test server independently:**
```bash
npx tsx mcp_server.ts
# Server should start without errors
```

## Troubleshooting

**Server not appearing in Claude:**
- Check Claude Desktop logs
- Verify paths are absolute in config
- Test server manually
- Ensure environment variables are set

**Commands always denied:**
- Use less strict template (`development` instead of `paranoid`)
- Review gatekeeper reasoning in logs
- Ensure OS detection is working

## Best Practices

1. **Start strict** - Use `paranoid` template initially
2. **Monitor logs** - Review what's being executed
3. **Limit scope** - Restrict paths with sandbox
4. **Test first** - Try the demo before production use

## Complete Examples

- **MCP Server:** [`cookbook/secureshell-ts/mcp_server.ts`](../cookbook/secureshell-ts/mcp_server.ts)
- **AI Agent Demo:** [`cookbook/secureshell-ts/mcp_client_demo.ts`](../cookbook/secureshell-ts/mcp_client_demo.ts)
- **Claude Config:** [`mcp_config.json`](../mcp_config.json)

## Next Steps

- [Security Templates](features/security-templates.md) - Configure security levels
- [LangChain Integration](integrations/langchain.md) - Alternative integration method
- [Zero-Trust Gatekeeper](features/gatekeeper.md) - How security works
