# Getting Started with SecureShell

This guide will help you get up and running with SecureShell in minutes.

## Installation

### TypeScript/JavaScript

```bash
npm install secureshell-ts
```

### Python

```bash
pip install secureshell
```

## Quick Start

### TypeScript

```typescript
import { SecureShell, OpenAIProvider } from 'secureshell-ts';

// Initialize with OpenAI provider
const shell = new SecureShell({
    provider: new OpenAIProvider({
        apiKey: process.env.OPENAI_API_KEY,
        model: 'gpt-4.1-mini'
    }),
    template: 'development'
});

// Execute a command with AI gatekeeping
const result = await shell.execute(
    'ls -la',
    'List files to check project structure'
);

if (result.success) {
    console.log(result.stdout);
} else {
    console.error('Blocked:', result.gatekeeper_reasoning);
}

await shell.close();
```

### Python

```python
import os
from secureshell import SecureShell
from secureshell.providers.openai import OpenAI

# Initialize with OpenAI provider
shell = SecureShell(
    template='development',
    provider=OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
)

# Execute a command
result = await shell.execute(
    command='ls -la',
    reasoning='List files to check project structure'
)

if result.success:
    print(result.stdout)
else:
    print(f"Blocked: {result.gatekeeper_reasoning}")

await shell.shutdown()
```

## Understanding the Flow

When you call `execute()`, SecureShell:

1. **Risk Classification** - Analyzes the command and assigns a risk tier (GREEN, YELLOW, RED)
2. **Sandbox Check** - Validates paths against allowed/blocked lists
3. **Config Check** - Checks allowlist/blocklist from configuration
4. **Gatekeeper Evaluation** - For YELLOW/RED commands, AI gatekeeper evaluates
5. **Execution** - If approved, command runs with timeout protection
6. **Audit Logging** - All executions are logged to JSONL

```
Command → Risk Classification → Sandbox → Config → Gatekeeper → Execute → Audit
```

## Security Templates

Instead of manually configuring everything, use a security template:

```typescript
// TypeScript
const shell = new SecureShell({ template: 'paranoid' });
```

```python
# Python
shell = SecureShell(template='paranoid')
```

Available templates:
- **`paranoid`** - Maximum security, blocks most commands
- **`production`** - Balanced for production environments
- **`development`** - Flexible for development
- **`ci_cd`** - Optimized for CI/CD pipelines

See [Security Templates](features/security-templates.md) for details.

## Environment Variables

Set your LLM provider API key:

```bash
# OpenAI
export OPENAI_API_KEY=sk-...

# Anthropic
export ANTHROPIC_API_KEY=sk-ant-...

# Google Gemini
export GOOGLE_API_KEY=...

# DeepSeek
export DEEPSEEK_API_KEY=...

# Groq
export GROQ_API_KEY=...
```

## Platform Awareness

SecureShell automatically detects your OS and blocks incompatible commands:

```typescript
// On Windows:
await shell.execute('rm -rf file.txt', 'Delete file');
// ❌ Blocked: "rm is a Unix command, use 'del' on Windows"

// On Linux/macOS:
await shell.execute('del file.txt', 'Delete file');
// ❌ Blocked: "del is a Windows command, use 'rm' on Unix"
```

See [Platform Awareness](features/platform-awareness.md) for more.

## Next Steps

- **Configure**: Learn about [Configuration](configuration.md) options
- **Explore Features**: Check out [Risk Classification](features/risk-classification.md), [Gatekeeper](features/gatekeeper.md), etc.
- **Try Providers**: Explore different [LLM Providers](providers/openai.md)
- **Integrate**: Use with [LangChain](integrations/langchain.md) or [MCP](mcp.md)
- **Examples**: Browse [working examples](../cookbook/)

## Common Issues

### "Gatekeeper disabled" warning

**Cause:** No valid LLM provider configured.

**Solution:** Set API key and specify provider:

```typescript
const shell = new SecureShell({
    provider: new OpenAIProvider({ apiKey: 'sk-...' })
});
```

### Commands always blocked

**Cause:** Using `paranoid` template or risk threshold too low.

**Solution:** Use a more permissive template or adjust risk threshold:

```typescript
const shell = new SecureShell({
    template: 'development',
    config: { riskThreshold: 'YELLOW' }
});
```

### Platform mismatch errors

**Cause:** Running Unix commands on Windows or vice versa.

**Solution:** SecureShell blocks these automatically. Let your agent see the error and self-correct, or use platform-aware command generation.

## Getting Help

- **Issues**: [GitHub Issues](https://github.com/divagr18/secureshell/issues)
- **Discussions**: [GitHub Discussions](https://github.com/divagr18/secureshell/discussions)
- **Examples**: [Examples Directory](../cookbook/)
