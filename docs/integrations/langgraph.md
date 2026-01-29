# LangGraph Integration

```typescript
import { SecureShell, OpenAIProvider, createSecureShellTool } from 'secureshell-ts';
import { ChatOpenAI } from '@langchain/openai';
import { StateGraph } from '@langchain/langgraph';

const shell = new SecureShell({
    provider: new OpenAIProvider({ apiKey: process.env.OPENAI_API_KEY }),
    template: 'development'
});

const tool = createSecureShellTool(shell);
const model = new ChatOpenAI({ modelName: 'gpt-4.1-mini' }).bindTools([tool]);

const workflow = new StateGraph({...})
    .addNode('agent', async (state) => {
        const result = await model.invoke(state.messages);
        return { messages: [result] };
    })
    .addNode('tools', toolNode);

const app = workflow.compile();
await app.invoke({ messages: [new HumanMessage('List files')] });
await shell.close();
```

**Examples:** [TypeScript](../../cookbook/secureshell-ts/integrations/langgraph.ts) | [Python](../../cookbook/integrations/langgraph_demo.py)
