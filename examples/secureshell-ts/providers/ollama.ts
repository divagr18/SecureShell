/**
 * Ollama Provider Example (Local LLM)
 * 
 * Demonstrates a local Ollama Agent utilizing SecureShell tools.
 * 
 * Usage:
 *   npx tsx examples/secureshell-ts/providers/ollama.ts
 */

import OpenAI from 'openai';
import { SecureShell, OpenAITools, OllamaProvider } from '@secureshell/ts';

async function main() {
    console.log('🤖 Ollama Local Agent + SecureShell Tools\n');

    // 1. Initialize SecureShell with Ollama provider
    const shell = new SecureShell({
        provider: new OllamaProvider({
            model: 'qwen2.5:14b',
            baseURL: 'http://localhost:11434/v1'
        }),
        osInfo: 'Windows'
    });

    // 2. Initialize Ollama Client (OpenAI compatible)
    const client = new OpenAI({
        baseURL: 'http://localhost:11434/v1',
        apiKey: 'ollama' // Not required
    });

    const tools = [OpenAITools.getToolDefinition() as any];

    const messages: OpenAI.Chat.Completions.ChatCompletionMessageParam[] = [
        { role: 'system', content: 'You are a helpful local assistant.' },
        { role: 'user', content: 'List files in the current directory' }
    ];

    console.log('User:', messages[1].content);

    const response = await client.chat.completions.create({
        model: 'qwen2.5:14b',
        messages: messages,
        tools: tools,
    });

    const message = response.choices[0]?.message;

    if (message?.tool_calls) {
        console.log(`\nAgent calling tool...`);
        const toolCall = message.tool_calls[0];

        if (toolCall.type === 'function') {
            const args = JSON.parse(toolCall.function.arguments);

            console.log(`> Command: ${args.command}`);
            console.log(`> Reasoning: ${args.reasoning}`);

            const result = await shell.execute(args.command, args.reasoning);
            console.log(result.success ? '✅ Success' : '❌ Failed');
            console.log('Output:', result.stdout.substring(0, 100) + '...');
        }
    } else {
        console.log('\nAgent:', message?.content || 'No response');
    }
}

main().catch(console.error);
