# Ollama Provider

```typescript
// TypeScript
import { SecureShell, OllamaProvider } from 'secureshell-ts';

const shell = new SecureShell({
    provider: new OllamaProvider({
        model: 'llama3',
        endpoint: 'http://localhost:11434'
    })
});
```

**Tool Usage:**
```typescript
import { OllamaTools } from 'secureshell-ts';

const tools = [OllamaTools.get_tool_definition()];

const response = await fetch('http://localhost:11434/api/chat', {
    method: 'POST',
    body: JSON.stringify({
        model: 'llama3',
        messages: [{ role: 'user', content: 'List files' }],
        tools: tools
    })
});

// Handle tool calls from response
```

**Examples:** [TypeScript](../../cookbook/secureshell-ts/providers/ollama.ts) | [Python](../../cookbook/providers/ollama.py)

