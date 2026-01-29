# OpenAI Provider

```typescript
// TypeScript
import { SecureShell, OpenAIProvider } from 'secureshell-ts';

const shell = new SecureShell({
    provider: new OpenAIProvider({
        apiKey: process.env.OPENAI_API_KEY,
        model: 'gpt-4.1-mini'
    })
});
```

```python
# Python
from secureshell import SecureShell
from secureshell.providers.openai import OpenAI

shell = SecureShell(
    provider=OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
)
```

**Tool Usage:**
```typescript
import { OpenAI } from 'openai';
import { OpenAITools } from 'secureshell-ts';

const client = new OpenAI();
const tools = [OpenAITools.get_tool_definition()];

const response = await client.chat.completions.create({
    model: 'gpt-4.1-mini',
    messages: [{ role: 'user', content: 'List files' }],
    tools: tools
});

// Handle tool calls
for (const toolCall of response.choices[0].message.tool_calls) {
    const result = await shell.handle_tool_call(toolCall);
}
```

**Examples:** [TypeScript](../../cookbook/secureshell-ts/providers/openai.ts) | [Python](../../cookbook/quickstart.py)
