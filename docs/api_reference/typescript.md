# TypeScript API Reference

## SecureShell Class

The main entry point for the library.

```typescript
import { SecureShell } from 'secureshell-ts';

const shell = new SecureShell(config?: SecureShellConfig);
```

### Methods

#### `execute(command: string, reasoning: string): Promise<ExecutionResult>`
Executes a shell command with gatekeeper evaluation.

- **command**: The shell command to run (e.g., "ls -la")
- **reasoning**: Context for why this command is needed (sent to gatekeeper)
- **Returns**: `Promise<ExecutionResult>`

#### `close(): Promise<void>`
Cleans up resources (audit logger, etc.). Always call this when done.

#### `getOSInfo(): string`
Returns the detected or configured OS string (e.g., "Windows 10").

---

## LLM Providers

Constructors for supported LLM providers.

### `OpenAIProvider`
```typescript
new OpenAIProvider({
    apiKey?: string;   // Defaults to process.env.OPENAI_API_KEY
    model?: string;    // Default: 'gpt-4o-mini'
    baseURL?: string;  // Optional custom endpoint
})
```

### `AnthropicProvider`
```typescript
new AnthropicProvider({
    apiKey?: string;   // Defaults to process.env.ANTHROPIC_API_KEY
    model?: string;    // Default: 'claude-3-5-sonnet-20241022'
})
```

### `GeminiProvider`
```typescript
new GeminiProvider({
    apiKey?: string;   // Defaults to process.env.GOOGLE_API_KEY
    model?: string;    // Default: 'gemini-1.5-flash'
})
```

### `OllamaProvider` (Local)
```typescript
new OllamaProvider({
    model?: string;    // Default: 'llama3'
    endpoint?: string; // Default: 'http://localhost:11434'
})
```

### Others
- `DeepSeekProvider({ apiKey, model })`
- `GroqProvider({ apiKey, model })`
- `LlamaCppProvider({ endpoint })`

---

## Tool Integrations

Helpers to create tools for other frameworks.

### LangChain
```typescript
import { createSecureShellTool } from 'secureshell-ts';

// Returns a DynamicStructuredTool compatible with LangChain agents
const tool = createSecureShellTool(shell);
```

### LangGraph
```typescript
// Create state graph node
const toolNode = createSecureShellTool(shell);

// Or use with tool calling agent
const model = new ChatOpenAI().bindTools([toolNode]);
```

### MCP (Model Context Protocol)
```typescript
import { createSecureShellMCPTool } from 'secureshell-ts';

// Returns an MCP-compatible tool wrapper
const mcpTool = createSecureShellMCPTool(shell);
```

---

## LLM Tools (for Manual Integration)

Helpers to generating tool definitions for specific providers.

- `OpenAITools.get_tool_definition()`
- `AnthropicTools.get_tool_definition()`
- `GeminiTools.get_tool_definition()`
- `DeepSeekTools.get_tool_definition()`
- `GroqTools.get_tool_definition()`
- `OllamaTools.get_tool_definition()`
- `LlamaCppTools.get_tool_definition()`

---

## Configuration

### `SecureShellConfig`

```typescript
interface SecureShellConfig {
    // Core
    debugMode?: boolean;      // Enable verbose logging
    provider?: BaseLLMProvider; // Custom provider instance

    // Security (Constructor args take precedence)
    allowedPaths?: string[];  // Whitelist paths
    blockedPaths?: string[];  // Blacklist paths
    allowlist?: string[];     // Always allow these commands
    blocklist?: string[];     // Always block these commands
    
    // Audit
    auditLogPath?: string;    // Path to log file
}
```

---

## Types

### `ExecutionResult`

```typescript
interface ExecutionResult {
    success: boolean;         // Did command succeed? (gatekeeper + execution)
    stdout: string;           // Standard output
    stderr: string;           // Standard error
    command: string;          // Original command
    risk_tier: RiskTier;      // GREEN, YELLOW, RED
    gatekeeper_reasoning?: string; // Why it was allowed/denied
}
```

### `RiskTier`

- `GREEN`: Safe, read-only (e.g., `ls`, `echo`)
- `YELLOW`: Needs review (e.g., `git push`, `npm install`)
- `RED`: Dangerous (e.g., `rm -rf`, `sudo`)
- `BLOCKED`: Always denied (e.g., `dd`, `fork bomb`)
