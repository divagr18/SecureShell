/**
 * LangGraph Integration Example for SecureShell TypeScript
 * 
 * Demonstrates how to use SecureShell with LangGraph for stateful agentic workflows.
 * 
 * Usage:
 *   export OPENAI_API_KEY=sk-...
 *   npx tsx integrations/langgraph.ts
 */

import 'dotenv/config';
import { SecureShell, OpenAIProvider, createSecureShellTool } from '@secureshell/ts';
import { createAgent } from 'langchain';

async function main() {
    if (!process.env.OPENAI_API_KEY) {
        console.error('❌ Set OPENAI_API_KEY');
        return;
    }

    console.log('🔐 SecureShell + LangGraph Integration\n');

    // Initialize SecureShell
    const shell = new SecureShell({
        provider: new OpenAIProvider({
            apiKey: process.env.OPENAI_API_KEY,
            model: 'gpt-4.1-mini'
        }),
        template: 'development',
        config: { debugMode: true }
    });

    // Create SecureShell tool using helper
    const shellTool = createSecureShellTool(shell);

    // Create agent with LangGraph
    const agent = createAgent({
        model: 'gpt-4.1-mini',
        tools: [shellTool]
    });

    // Test the workflow
    console.log('Testing: Multi-step workflow with SecureShell\n');
    console.log('Task: List files and check current directory\n');

    const result = await agent.invoke({
        messages: [
            {
                role: 'user',
                content: 'Please list the files in the current directory and then show me the current working directory path'
            }
        ]
    });

    console.log('\n✅ Workflow completed');
    console.log('Total messages:', result.messages.length);

    await shell.close();
}

main().catch(console.error);
