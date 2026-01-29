/**
 * SecureShell TypeScript Quickstart Example
 * 
 * This demonstrates the basic usage of SecureShell with OpenAI.
 * 
 * Usage:
 *   export OPENAI_API_KEY=sk-...
 *   npm install
 *   npx tsx examples/quickstart.ts
 */

import 'dotenv/config';
import { SecureShell, OpenAIProvider } from '@secureshell/ts';


async function main() {
    console.log('🔐 SecureShell TypeScript Quickstart\n');

    // Initialize SecureShell with OpenAI provider
    const shell = new SecureShell({
        provider: new OpenAIProvider({
            apiKey: process.env.OPENAI_API_KEY!,
            model: 'gpt-4.1-mini'
        }),
        template: 'development', // Use development template (optional)
        osInfo: 'Windows 11' // Tell gatekeeper what OS we're on (optional)
    });

    console.log('--- Example 1: Safe Read Command ---');
    const result1 = await shell.execute(
        'dir',
        'List files in current directory to see what we have'
    );

    console.log('Success:', result1.success);
    console.log('Output:', result1.stdout.substring(0, 500));
    console.log('Decision:', result1.gatekeeper_decision);
    console.log('');

    console.log('--- Example 2: Risky Command (Should be blocked) ---');
    const result2 = await shell.execute(
        'rm -rf /',
        'Delete everything (bad idea!)'
    );

    console.log('Success:', result2.success);
    console.log('Error:', result2.stderr);
    console.log('Decision:', result2.gatekeeper_decision);
    console.log('');

    console.log('--- Example 3: Moderate Risk Command ---');
    const result3 = await shell.execute(
        'echo "Hello SecureShell" > test.txt',
        'Create a test file to verify write permissions'
    );

    console.log('Success:', result3.success);
    console.log('Output:', result3.stdout || result3.stderr);
    console.log('GK Reasoning:', result3.gatekeeper_reasoning);
    console.log('');

    // Cleanup
    await shell.close();
}

main().catch(console.error);
