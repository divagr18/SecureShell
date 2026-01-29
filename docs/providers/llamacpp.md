# LlamaCpp Provider

```typescript
// TypeScript
import { SecureShell, LlamaCppProvider } from 'secureshell-ts';

const shell = new SecureShell({
    provider: new LlamaCppProvider({
        endpoint: 'http://localhost:8080'
    })
});
```

**Tool Usage:**
```typescript
import { LlamaCppTools } from 'secureshell-ts';

const tools = [LlamaCppTools.get_tool_definition()];

const response = await fetch('http://localhost:8080/v1/chat/completions', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        messages: [{ role: 'user', content: 'List files' }],
        tools: tools
    })
});

// Handle tool calls from response
```

**Examples:** [TypeScript](../../cookbook/secureshell-ts/providers/llamacpp.ts) | [Python](../../cookbook/providers/llamacpp.py)

