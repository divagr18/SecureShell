/**
 * OpenAI Provider Example for SecureShell TypeScript
 * 
 * Demonstrates an OpenAI Agent using SecureShell as a tool.
 * 
 * Usage:
 *   export OPENAI_API_KEY=sk-...
 *   npx tsx examples/secureshell-ts/providers/openai.ts
 */

import 'dotenv/config';
import OpenAI from 'openai';
import { SecureShell, OpenAITools, OpenAIProvider } from 'secureshell-ts';

async function main() {
    console.log('🤖 OpenAI Agent + SecureShell Tools Demo\n');

    // 1. Initialize SecureShell (The Gatekeeper)
    const shell = new SecureShell({
        provider: new OpenAIProvider({
            apiKey: process.env.OPENAI_API_KEY!,
            model: 'gpt-4.1-mini' // Gatekeeper model
        }),
        template: 'development',
        osInfo: 'Windows'
    });

    // 2. Initialize OpenAI Client (The Agent)
    const client = new OpenAI({
        apiKey: process.env.OPENAI_API_KEY
    });

    // 3. Define Tools
    const tools = [OpenAITools.getToolDefinition() as any];

    const messages: OpenAI.Chat.Completions.ChatCompletionMessageParam[] = [
        { role: 'system', content: 'You are a helpful assistant. Use the shell tool to answer questions.' },
        { role: 'user', content: 'List the files in the current directory and read package.json' }
    ];

    console.log('User:', messages[1].content);

    // 4. Agent Loop
    while (true) {
        const response = await client.chat.completions.create({
            model: 'gpt-4.1-mini', // Agent model
            messages: messages,
            tools: tools,
        });

        const message = response.choices[0].message;
        messages.push(message);

        if (message.tool_calls) {
            console.log(`\nAgent calling ${message.tool_calls.length} tool(s)...`);

            for (const toolCall of message.tool_calls) {
                if (toolCall.type === 'function' && toolCall.function.name === 'execute_shell_command') {
                    const args = JSON.parse(toolCall.function.arguments);
                    console.log(`> Executing: ${args.command}`);
                    console.log(`> Reasoning: ${args.reasoning}`);

                    // Execute via SecureShell
                    const result = await shell.execute(args.command, args.reasoning);

                    let output;
                    if (result.success) {
                        output = result.stdout;
                        console.log('✅ Result:', output.substring(0, 50) + '...');
                    } else {
                        output = `Error: ${result.stderr} (Gatekeeper: ${result.gatekeeper_decision})`;
                        console.log('❌ Blocked:', output);
                    }

                    messages.push({
                        role: 'tool',
                        tool_call_id: toolCall.id,
                        content: output
                    });
                }
            }
        } else {
            console.log('\nAgent:', message.content);
            break;
        }
    }
}

main().catch(console.error);
