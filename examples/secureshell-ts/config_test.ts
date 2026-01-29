/**
 * Config Test - YAML Configuration Demo for SecureShell TypeScript
 * 
 * Demonstrates allowlist/blocklist feature with command type matching.
 * 
 * Usage:
 *   npx tsx examples/secureshell-ts/features/config_test.ts
 */

import { SecureShell } from '@secureshell/ts';

async function main() {
    console.log('🚀 Testing Allowlist/Blocklist with Command Types\n');

    // Initialize shell without provider (testing config only)
    const shell = new SecureShell({
        config: {
            debugMode: true,
            allowlist: ['echo', 'ls', 'dir'],
            blocklist: ['rm', 'dd']
        }
    });

    console.log('Loaded config:');
    console.log(`Allowlist: ${JSON.stringify(shell.config.allowlist)}`);
    console.log(`Blocklist: ${JSON.stringify(shell.config.blocklist)}\n`);

    // Test 1: Allowlisted command type
    console.log('--- Test 1: Allowlisted Command Type ---');
    const res1 = await shell.execute('echo "This should work"', 'testing allowlist');
    console.log('Success:', res1.success);
    console.log('Risk Tier:', res1.risk_tier);
    console.log('Output:', res1.success ? res1.stdout : res1.stderr, '\n');

    // Test 2: Blocklisted command type
    console.log('--- Test 2: Blocklisted Command Type ---');
    const res2 = await shell.execute('rm some_file.txt', 'trying to delete');
    console.log('Success:', res2.success);
    console.log('Reason:', res2.stderr, '\n');

    // Test 3: Another allowlisted command
    console.log('--- Test 3: Another Allowlisted Command ---');
    const res3 = await shell.execute('dir', 'listing files');
    console.log('Success:', res3.success);
    console.log('Output:', res3.success ? res3.stdout.substring(0, 100) : res3.stderr);

    await shell.close();
}

main().catch(console.error);
