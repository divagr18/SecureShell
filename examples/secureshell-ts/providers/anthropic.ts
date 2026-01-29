/**
 * Anthropic Claude Provider Example for SecureShell TypeScript
 * 
 * Demonstrates a Claude Agent using SecureShell as a tool.
 * 
 * Usage:
 *   export ANTHROPIC_API_KEY=sk-ant-...
 *   npx tsx examples/secureshell-ts/providers/anthropic.ts
 */

import 'dotenv/config';
import Anthropic from '@anthropic-ai/sdk';
import { SecureShell, AnthropicTools, AnthropicProvider } from 'secureshell-ts';

async function main() {
    console.log('🤖 Anthropic Claude Agent + SecureShell Tools Demo\n');

    // 1. Initialize SecureShell
    const shell = new SecureShell({
        provider: new AnthropicProvider({
            apiKey: process.env.ANTHROPIC_API_KEY!,
            model: 'claude-sonnet-4-5'
        }),
        osInfo: 'Windows'
    });

    // 2. Initialize Anthropic Client
    const client = new Anthropic({
        apiKey: process.env.ANTHROPIC_API_KEY
    });

    // 3. Define Tools
    const tool = AnthropicTools.getToolDefinition();

    const messages: Anthropic.MessageParam[] = [
        { role: 'user', content: 'What files are in the current directory?' }
    ];

    console.log('User:', messages[0].content);

    // 4. Agent Loop
    let currentMessages = messages;

    for (let i = 0; i < 5; i++) { // Max iterations
        const response = await client.messages.create({
            model: 'claude-sonnet-4-5',
            max_tokens: 1024,
            tools: [tool],
            messages: currentMessages
        });

        console.log(`\nResponse Stop Reason: ${response.stop_reason}`);

        // Check for tool use
        const toolUseBlock = response.content.find(block => block.type === 'tool_use');

        if (toolUseBlock && toolUseBlock.type === 'tool_use') {
            console.log(`> Agent requesting tool execution: ${toolUseBlock.name}`);

            if (toolUseBlock.name === 'execute_shell_command') {
                const args = toolUseBlock.input as { command: string; reasoning: string };
                console.log(`> Command: ${args.command}`);
                console.log(`> Reasoning: ${args.reasoning}`);

                // Execute via SecureShell
                const result = await shell.execute(args.command, args.reasoning);

                const output = result.success ? result.stdout : `Error: ${result.stderr}`;
                console.log(result.success ? '✅ Result: Success' : '❌ Result: Blocked/Failed');

                // Add assistant response and tool result to history
                currentMessages.push({
                    role: 'assistant',
                    content: response.content
                });

                currentMessages.push({
                    role: 'user',
                    content: [{
                        type: 'tool_result',
                        tool_use_id: toolUseBlock.id,
                        content: output
                    }]
                });
            }
        } else {
            // Final response
            const textBlock = response.content.find(block => block.type === 'text');
            if (textBlock && textBlock.type === 'text') {
                console.log('\nAgent:', textBlock.text);
            }
            break;
        }
    }
}

main().catch(console.error);
