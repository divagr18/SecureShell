# Google Gemini Provider

```typescript
// TypeScript
import { SecureShell, GeminiProvider } from 'secureshell-ts';

const shell = new SecureShell({
    provider: new GeminiProvider({
        apiKey: process.env.GOOGLE_API_KEY,
        model: 'gemini-2.5-flash'
    })
});
```

```python
# Python
from secureshell import SecureShell
from secureshell.providers.gemini import Gemini

shell = SecureShell(
    provider=Gemini(api_key=os.getenv("GOOGLE_API_KEY"))
)
```

**Tool Usage:**
```typescript
import { GoogleGenerativeAI } from '@google/generative-ai';
import { GeminiTools } from 'secureshell-ts';

const genAI = new GoogleGenerativeAI(process.env.GOOGLE_API_KEY);
const model = genAI.getGenerativeModel({
    model: 'gemini-2.5-flash',
    tools: [GeminiTools.get_tool_definition()]
});

const result = await model.generateContent('List files');

// Handle tool calls
for (const call of result.response.functionCalls()) {
    const output = await shell.handle_tool_call(call);
}
```

**Examples:** [TypeScript](../../cookbook/secureshell-ts/providers/gemini.ts) | [Python](../../cookbook/providers/gemini.py)
