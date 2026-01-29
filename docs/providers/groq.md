# Groq Provider

```typescript
// TypeScript
import { SecureShell, GroqProvider } from 'secureshell-ts';

const shell = new SecureShell({
    provider: new GroqProvider({
        apiKey: process.env.GROQ_API_KEY,
        model: 'llama-3.3-70b-versatile'
    })
});
```

**Tool Usage:**
```typescript
import { OpenAI } from 'openai';
import { GroqTools } from 'secureshell-ts';

const client = new OpenAI({
    apiKey: process.env.GROQ_API_KEY,
    baseURL: 'https://api.groq.com/openai/v1'
});

const tools = [GroqTools.get_tool_definition()];

const response = await client.chat.completions.create({
    model: 'llama-3.3-70b-versatile',
    messages: [{ role: 'user', content: 'List files' }],
    tools: tools
});

// Handle tool calls
for (const toolCall of response.choices[0].message.tool_calls) {
    const result = await shell.handle_tool_call(toolCall);
}
```

**Examples:** [TypeScript](../../cookbook/secureshell-ts/providers/groq.ts) | [Python](../../cookbook/providers/groq.py)

