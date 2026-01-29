# LangChain Integration

```typescript
import { SecureShell, OpenAIProvider, createSecureShellTool } from 'secureshell-ts';
import { ChatOpenAI } from '@langchain/openai';
import { AgentExecutor, createToolCallingAgent } from 'langchain/agents';

const shell = new SecureShell({
    provider: new OpenAIProvider({ apiKey: process.env.OPENAI_API_KEY }),
    template: 'development'
});

const tool = createSecureShellTool(shell);
const model = new ChatOpenAI({ modelName: 'gpt-4.1-mini' });
const agent = await createToolCallingAgent({ llm: model, tools: [tool], prompt });
const executor = new AgentExecutor({ agent, tools: [tool] });

await executor.invoke({ input: 'List the files in the current directory' });
await shell.close();
```

**Examples:** [TypeScript](../../cookbook/secureshell-ts/integrations/langchain.ts) | [Python](../../cookbook/integrations/langchain_demo.py)
