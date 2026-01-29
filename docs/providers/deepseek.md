# DeepSeek Provider

```typescript
// TypeScript
import { SecureShell, DeepSeekProvider } from 'secureshell-ts';

const shell = new SecureShell({
    provider: new DeepSeekProvider({
        apiKey: process.env.DEEPSEEK_API_KEY,
        model: 'deepseek-chat'
    })
});
```

**Tool Usage:**
```typescript
import { OpenAI } from 'openai';
import { DeepSeekTools } from 'secureshell-ts';

const client = new OpenAI({
    apiKey: process.env.DEEPSEEK_API_KEY,
    baseURL: 'https://api.deepseek.com'
});

const tools = [DeepSeekTools.get_tool_definition()];

const response = await client.chat.completions.create({
    model: 'deepseek-chat',
    messages: [{ role: 'user', content: 'List files' }],
    tools: tools
});

// Handle tool calls
for (const toolCall of response.choices[0].message.tool_calls) {
    const result = await shell.handle_tool_call(toolCall);
}
```

**Examples:** [TypeScript](../../cookbook/secureshell-ts/providers/deepseek.ts) | [Python](../../cookbook/providers/deepseek.py)

