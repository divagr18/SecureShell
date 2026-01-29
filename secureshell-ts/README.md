# SecureShell TypeScript SDK

AI-powered command execution with intelligent security gatekeeping. SecureShell uses LLMs to evaluate commands before execution, providing adaptive protection against dangerous operations while maintaining developer productivity.

[![npm version](https://badge.fury.io/js/secureshell-ts.svg)](https://www.npmjs.com/package/secureshell-ts)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- 🤖 **AI-Powered Gatekeeper** - LLM evaluates every command for safety
- 🔒 **Multi-Tier Risk Classification** - GREEN, YELLOW, RED risk levels
- 🌍 **Platform-Aware** - Automatic OS detection and platform-specific command validation
- 🔌 **7 LLM Providers** - OpenAI, Anthropic, Gemini, DeepSeek, Groq, Ollama, LlamaCpp
- 🛠️ **Framework Integrations** - LangChain, LangGraph, MCP (Model Context Protocol)
- 📝 **Comprehensive Audit Logging** - JSONL format with automatic rotation
- ⚙️ **Flexible Configuration** - YAML, environment variables, or programmatic
- 🎯 **Security Templates** - Paranoid, Production, Development, CI/CD profiles

## Installation

```bash
npm install secureshell-ts
```

## Quick Start

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

## Platform-Aware Command Evaluation

SecureShell automatically detects your OS and blocks platform-incompatible commands:

```typescript
// On Windows, this will be DENIED by the gatekeeper
const result = await shell.execute('rm -rf file.txt', 'Delete file');
// Gatekeeper: "DENY - rm is a Unix command that will fail on Windows"

// The gatekeeper suggests Windows alternatives
// Agent can self-correct and try: 'del file.txt'
```

## Supported LLM Providers

```typescript
import { 
    OpenAIProvider,
    AnthropicProvider,
    GeminiProvider,
    DeepSeekProvider,
    GroqProvider,
    OllamaProvider,
    LlamaCppProvider
} from 'secureshell-ts';

// OpenAI (GPT-4, GPT-4o, etc.)
new OpenAIProvider({ apiKey: '...', model: 'gpt-4.1-mini' })

// Anthropic Claude
new AnthropicProvider({ apiKey: '...', model: 'claude-sonnet-4-5' })

// Google Gemini
new GeminiProvider({ apiKey: '...', model: 'gemini-2.5-flash' })

// DeepSeek
new DeepSeekProvider({ apiKey: '...', model: 'deepseek-chat' })

// Groq
new GroqProvider({ apiKey: '...', model: 'llama-3.3-70b-versatile' })

// Ollama (local)
new OllamaProvider({ model: 'llama3', endpoint: 'http://localhost:11434' })

// LlamaCpp (local)
new LlamaCppProvider({ model: 'llama3', endpoint: 'http://localhost:8080' })
```

## Framework Integrations

### LangChain

```typescript
import { SecureShell, OpenAIProvider, createSecureShellTool } from 'secureshell-ts';
import { createAgent } from 'langchain';

const shell = new SecureShell({
    provider: new OpenAIProvider({ apiKey: process.env.OPENAI_API_KEY }),
    template: 'development',
    config: { debugMode: true }
});

const tool = createSecureShellTool(shell);

const agent = createAgent({
    model: 'gpt-4.1-mini',
    tools: [tool]
});

await agent.invoke({
    messages: [{ role: 'user', content: 'List files in current directory' }]
});
```

### MCP (Model Context Protocol)

```typescript
import { SecureShell, OpenAIProvider, createSecureShellMCPTool } from 'secureshell-ts';
import { Server } from '@modelcontextprotocol/sdk/server/index.js';

const shell = new SecureShell({
    provider: new OpenAIProvider({ apiKey: process.env.OPENAI_API_KEY }),
    template: 'development'
});

const server = new Server({ name: 'secureshell-mcp', version: '0.1.0' }, { capabilities: { tools: {} } });
const mcpTool = createSecureShellMCPTool(shell);

// Register tool with MCP server
server.setRequestHandler(ListToolsRequestSchema, async () => ({
    tools: [{ name: mcpTool.name, description: mcpTool.description, inputSchema: mcpTool.inputSchema }]
}));
```

## Security Templates

Choose a security profile that fits your use case:

```typescript
// Maximum security - blocks most commands
new SecureShell({ template: 'paranoid' })

// Balanced for production
new SecureShell({ template: 'production' })

// Flexible for development
new SecureShell({ template: 'development' })

// Automation-friendly
new SecureShell({ template: 'ci_cd' })
```

## Configuration

### YAML Configuration

```yaml
# secureshell.yaml
security:
  gatekeeper_enabled: true
  risk_threshold: "YELLOW"
  allowlist:
    - "ls"
    - "pwd"
    - "echo"
  blocklist:
    - "rm -rf /"
    - "dd"
  sandbox:
    allowed_paths:
      - "/workspace"
    blocked_paths:
      - "/etc"
      - "/sys"
```

```typescript
import { loadConfig } from 'secureshell-ts';

const config = loadConfig('./secureshell.yaml');
const shell = new SecureShell({ config });
```

### Programmatic Configuration

```typescript
const shell = new SecureShell({
    config: {
        debugMode: true,
        riskThreshold: 'YELLOW',
        allowlist: ['ls', 'pwd', 'cat'],
        blocklist: ['rm', 'dd'],
        sandbox: {
            allowedPaths: ['/workspace'],
            blockedPaths: ['/etc', '/sys']
        }
    }
});
```

## Audit Logging

All command executions are logged in JSONL format:

```json
{
  "timestamp": "2026-01-30T01:00:00.000Z",
  "command": "ls -la",
  "risk_tier": "GREEN",
  "gatekeeper_decision": "ALLOW",
  "success": true,
  "exit_code": 0
}
```

Logs are automatically rotated when they exceed the configured size limit.

## Examples

The SDK includes comprehensive examples in the repository:

- **Provider Examples** - All 7 LLM providers
- **Integration Examples** - LangChain, LangGraph, MCP
- **Feature Demos** - Templates, allowlist/blocklist, challenge mode

## API Reference

### SecureShell

```typescript
class SecureShell {
    constructor(options?: {
        provider?: BaseLLMProvider;
        config?: SecureShellConfig;
        template?: SecurityTemplate;
        allowedPaths?: string[];
        blockedPaths?: string[];
        osInfo?: string;
    });

    async execute(command: string, reasoning: string): Promise<ExecutionResult>;
    async close(): Promise<void>;
    getOSInfo(): string;
}
```

### ExecutionResult

```typescript
interface ExecutionResult {
    success: boolean;
    command: string;
    stdout: string;
    stderr: string;
    exit_code: number;
    risk_tier: RiskTier;
    gatekeeper_decision?: GatekeeperDecision;
    gatekeeper_reasoning?: string;
}
```

## License

MIT © SecureShell Contributors

## Contributing

Contributions welcome! Please read our contributing guidelines and submit pull requests to our repository.

## Support

- 📖 [Documentation](https://github.com/divagr18/secureshell)
- 🐛 [Issue Tracker](https://github.com/divagr18/secureshell/issues)
- 💬 [Discussions](https://github.com/divagr18/secureshell/discussions)
