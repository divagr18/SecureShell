/**
 * Groq Provider Example for SecureShell TypeScript
 * 
 * Demonstrates a Groq Agent (OpenAI-compatible) using SecureShell.
 * 
 * Usage:
 *   export GROQ_API_KEY=gsk_...
 *   npx tsx examples/secureshell-ts/providers/groq.ts
 */

import 'dotenv/config';
import OpenAI from 'openai';
import { SecureShell, OpenAITools, GroqProvider } from 'secureshell-ts';

async function main() {
    console.log('🤖 Groq Agent + SecureShell Tools Demo\n');

    // 1. Initialize SecureShell (auto-detects OS)
    const shell = new SecureShell({
        provider: new GroqProvider({
            apiKey: process.env.GROQ_API_KEY!
        })
    });

    // 2. Initialize Groq Client
    const client = new OpenAI({
        apiKey: process.env.GROQ_API_KEY,
        baseURL: 'https://api.groq.com/openai/v1'
    });

    // 3. Define Tools
    const tools = [OpenAITools.getToolDefinition() as any];

    const messages: OpenAI.Chat.Completions.ChatCompletionMessageParam[] = [
        { role: 'system', content: 'You are a fast assistant. Use shell commands to help the user.' },
        { role: 'user', content: 'Find all TypeScript files in the current directory' }
    ];

    console.log('User:', messages[1].content, '\n');

    // 4. Multi-turn Agent Loop
    for (let turn = 0; turn < 5; turn++) {
        const response = await client.chat.completions.create({
            model: 'llama-3.3-70b-versatile',
            messages: messages,
            tools: tools,
        });

        const message = response.choices[0].message;
        messages.push(message);

        if (message.tool_calls) {
            console.log(`\nTurn ${turn + 1}: Agent calling ${message.tool_calls.length} tool(s)...`);

            for (const toolCall of message.tool_calls) {
                if (toolCall.type === 'function' && toolCall.function.name === 'execute_shell_command') {
                    const args = JSON.parse(toolCall.function.arguments);
                    console.log(`> Command: ${args.command}`);
                    console.log(`> Reasoning: ${args.reasoning}`);

                    const result = await shell.execute(args.command, args.reasoning);
                    const output = result.success ? result.stdout : `Error: ${result.stderr}`;

                    console.log(result.success ? '✅ Success' : '❌ Blocked/Failed');
                    console.log('Output:', output.substring(0, 150));

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
