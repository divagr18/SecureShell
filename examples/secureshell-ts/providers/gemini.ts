/**
 * Google Gemini Provider Example for SecureShell TypeScript
 * 
 * Demonstrates a Gemini Agent using SecureShell as a tool with the new @google/genai SDK.
 * 
 * Usage:
 *   export GEMINI_API_KEY=AIza...
 *   npx tsx examples/secureshell-ts/providers/gemini.ts
 */

import { config } from 'dotenv';
import { GoogleGenAI, FunctionCallingConfigMode, type Content } from '@google/genai';
import { SecureShell, GeminiTools, GeminiProvider } from '@secureshell/ts';

// Load .env from project root
config({ path: '../../.env' });

async function main() {
    console.log('🤖 Gemini Agent + SecureShell Tools Demo (@google/genai)\n');

    // API key can be either GEMINI_API_KEY or GOOGLE_API_KEY
    const apiKey = process.env.GEMINI_API_KEY || process.env.GOOGLE_API_KEY;

    // 1. Initialize SecureShell (auto-detects OS)
    const shell = new SecureShell({
        provider: new GeminiProvider({
            apiKey: apiKey!,
            model: 'gemini-2.5-flash'
        })
    });

    // 2. Initialize Gemini Client
    const genAI = new GoogleGenAI({ apiKey });

    // 3. Define Tools
    const toolDefinition = GeminiTools.getToolDefinition();

    // 4. Conversation History
    const history: Content[] = [
        {
            role: 'user',
            parts: [{
                text: 'List files in the current directory and show me the contents of package.json.'
            }]
        }
    ];

    console.log('User: List files and show package.json\n');

    // 5. Multi-turn Agent Loop
    for (let turn = 0; turn < 5; turn++) {
        const result = await genAI.models.generateContent({
            model: 'gemini-2.5-flash',
            contents: history,
            config: {
                tools: [{
                    functionDeclarations: [toolDefinition]
                }],
                toolConfig: {
                    functionCallingConfig: {
                        mode: FunctionCallingConfigMode.AUTO
                    }
                }
            }
        });

        const functionCalls = result.functionCalls;
        const text = result.text;

        // Add model response to history
        const modelParts: any[] = [];
        if (text) {
            modelParts.push({ text });
        }
        if (functionCalls && functionCalls.length > 0) {
            for (const call of functionCalls) {
                modelParts.push({
                    functionCall: {
                        name: call.name,
                        args: call.args
                    }
                });
            }
        }
        history.push({ role: 'model', parts: modelParts });

        if (functionCalls && functionCalls.length > 0) {
            console.log(`\nTurn ${turn + 1}: Agent calling ${functionCalls.length} tool(s)...`);

            const functionResponses: any[] = [];

            for (const call of functionCalls) {
                if (call.name === 'execute_shell_command') {
                    const args = call.args as { command: string; reasoning: string };
                    console.log(`> Executing: ${args.command}`);
                    console.log(`> Reasoning: ${args.reasoning}`);

                    const execResult = await shell.execute(args.command, args.reasoning);
                    const output = execResult.success ? execResult.stdout : `Error: ${execResult.stderr}`;

                    console.log(execResult.success ? '✅ Success' : '❌ Blocked/Failed');
                    console.log('Output:', output.substring(0, 150));

                    functionResponses.push({
                        functionResponse: {
                            name: call.name,
                            response: { result: output }
                        }
                    });
                }
            }

            // Add function responses to history
            history.push({ role: 'user', parts: functionResponses });
        } else if (text) {
            console.log('\nAgent:', text);
            break;
        }
    }
}

main().catch(console.error);
