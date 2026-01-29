/**
 * LlamaCpp Provider Example (Local)
 * 
 * Demonstrates a local llama.cpp Agent utilizing SecureShell tools.
 * 
 * Usage:
 *   npx tsx examples/secureshell-ts/providers/llamacpp.ts
 */

import OpenAI from 'openai';
import { SecureShell, OpenAITools, LlamaCppProvider } from '@secureshell/ts';

async function main() {
    console.log('🤖 llama.cpp Agent + SecureShell Tools\n');

    const shell = new SecureShell({
        provider: new LlamaCppProvider({
            baseURL: 'http://localhost:8080/v1'
        }),
        osInfo: 'Windows'
    });

    const client = new OpenAI({
        baseURL: 'http://localhost:8080/v1',
        apiKey: 'sk-no-key-required'
    });

    const tools = [OpenAITools.getToolDefinition() as any];

    const response = await client.chat.completions.create({
        model: 'gpt-3.5-turbo', // Generic name often used by llama.cpp server
        messages: [
            { role: 'user', content: 'Echo "Hello from Local LLM"' }
        ],
        tools: tools,
    });

    const message = response.choices[0]?.message;

    if (message?.tool_calls) {
        const toolCall = message.tool_calls[0];
        if (toolCall.type === 'function') {
            const args = JSON.parse(toolCall.function.arguments);
            console.log(`Agent executing: ${args.command}`);

            const result = await shell.execute(args.command, args.reasoning);
            console.log('Output:', result.stdout);
        }
    } else {
        console.log('Agent:', message?.content);
    }
}

main().catch(console.error);
