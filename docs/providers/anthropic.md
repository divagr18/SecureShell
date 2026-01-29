# Anthropic Provider

```typescript
// TypeScript
import { SecureShell, AnthropicProvider } from 'secureshell-ts';

const shell = new SecureShell({
    provider: new AnthropicProvider({
        apiKey: process.env.ANTHROPIC_API_KEY,
        model: 'claude-sonnet-4-5'
    })
});
```

```python
# Python
from secureshell import SecureShell
from secureshell.providers.anthropic import Anthropic

shell = SecureShell(
    provider=Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
)
```

**Tool Usage:**
```typescript
import { Anthropic } from '@anthropic-ai/sdk';
import { AnthropicTools } from 'secureshell-ts';

const client = new Anthropic();
const tools = [AnthropicTools.get_tool_definition()];

const response = await client.messages.create({
    model: 'claude-sonnet-4-5',
    messages: [{ role: 'user', content: 'List files' }],
    tools: tools
});

// Handle tool calls
for (const content of response.content) {
    if (content.type === 'tool_use') {
        const result = await shell.handle_tool_call(content);
    }
}
```

**Examples:** [TypeScript](../../cookbook/secureshell-ts/providers/anthropic.ts) | [Python](../../cookbook/providers/anthropic.py)
