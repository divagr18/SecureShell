/**
 * Challenge Mode Demo for SecureShell TypeScript
 * 
 * Demonstrates the CHALLENGE gatekeeper decision type.
 * The gatekeeper returns CHALLENGE when:
 * - Reasoning is vague or unclear
 * - Intent is ambiguous
 * - More information is needed
 * 
 * Usage:
 *   export OPENAI_API_KEY=sk-...
 *   npx tsx examples/secureshell-ts/features/challenge_demo.ts
 */

import 'dotenv/config';
import { SecureShell, OpenAIProvider } from '@secureshell/ts';

async function main() {
    if (!process.env.OPENAI_API_KEY) {
        console.error('❌ Set OPENAI_API_KEY');
        return;
    }

    console.log('🚀 Challenge Mode Demo\n');

    const shell = new SecureShell({
        provider: new OpenAIProvider({
            apiKey: process.env.OPENAI_API_KEY,
            model: 'gpt-4.1-mini'
        }),
        config: {
            debugMode: true
        }
    });

    // Test 1: Clear reasoning (should ALLOW)
    console.log('--- Test 1: Clear Reasoning (Should ALLOW) ---');
    const res1 = await shell.execute(
        'dir',
        'List directory contents to understand project structure for development'
    );
    console.log('Success:', res1.success);
    console.log('Decision:', res1.gatekeeper_decision || 'N/A', '\n');

    // Test 2: Vague reasoning (may CHALLENGE)
    console.log('--- Test 2: Vague Reasoning (May CHALLENGE) ---');
    const res2 = await shell.execute(
        'rm temp.txt',
        'just testing'
    );
    console.log('Success:', res2.success);
    console.log('Decision:', res2.gatekeeper_decision || 'N/A');
    console.log('Reason:', res2.stderr || res2.gatekeeper_reasoning);
    if (res2.required_clarification) {
        console.log('Clarification needed:', res2.required_clarification);
    }
    console.log('');

    // Test 3: Ambiguous intent (may CHALLENGE)
    console.log('--- Test 3: Ambiguous Intent (May CHALLENGE) ---');
    const res3 = await shell.execute(
        'git reset --hard',
        'need to fix something'
    );
    console.log('Success:', res3.success);
    console.log('Decision:', res3.gatekeeper_decision || 'N/A');
    console.log('Reason:', res3.stderr || res3.gatekeeper_reasoning);
    if (res3.required_clarification) {
        console.log('Clarification needed:', res3.required_clarification);
    }
    console.log('');

    await shell.close();
}

main().catch(console.error);
