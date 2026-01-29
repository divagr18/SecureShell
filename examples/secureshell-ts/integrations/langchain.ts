/**
 * LangChain Integration Example for SecureShell TypeScript
 * 
 * Demonstrates how to use SecureShell with LangChain agents.
 * 
 * Usage:
 *   export OPENAI_API_KEY=sk-...
 *   npx tsx integrations/langchain.ts
 */

import 'dotenv/config';
import { SecureShell, OpenAIProvider } from 'secureshell-ts';
import { createAgent, tool } from 'langchain';
import * as z from 'zod';

async function main() {
    if (!process.env.OPENAI_API_KEY) {
        console.error('❌ Set OPENAI_API_KEY');
        return;
    }

    // Initialize SecureShell with debug mode
    const shell = new SecureShell({
        provider: new OpenAIProvider({
            apiKey: process.env.OPENAI_API_KEY,
            model: 'gpt-4.1-mini'
        }),
        template: 'development',
        config: { debugMode: true }  // Disable verbose logs
    });

    // Create SecureShell tool using LangChain tool API
    const executeCommand = tool(
        async (input) => {
            const result = await shell.execute(input.command, input.reasoning);

            if (result.success) {
                return JSON.stringify({
                    success: true,
                    stdout: result.stdout,
                    stderr: result.stderr
                });
            } else {
                return JSON.stringify({
                    success: false,
                    error: result.stderr,
                    gatekeeper_decision: result.gatekeeper_decision,
                    gatekeeper_reasoning: result.gatekeeper_reasoning
                });
            }
        },
        {
            name: 'execute_shell_command',
            description: 'Execute a shell command safely with AI gatekeeping. You MUST provide clear reasoning.',
            schema: z.object({
                command: z.string().describe('The shell command to execute'),
                reasoning: z.string().min(10).describe('Detailed explanation of why this command is necessary')
            })
        }
    );

    // Create agent
    const agent = createAgent({
        model: 'gpt-4.1-mini',
        tools: [executeCommand]
    });

    // Test the agent
    const result = await agent.invoke({
        messages: [{ role: 'user', content: 'List the files in the current directory' }]
    });

    await shell.close();
}

main().catch(console.error);
