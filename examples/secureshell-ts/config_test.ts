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
    // Initialize shell with debug mode (SDK will log everything)
    const shell = new SecureShell({
        config: {
            debugMode: true,  // SDK handles all logging
            allowlist: ['echo', 'ls', 'dir'],
            blocklist: ['rm', 'dd']
        }
    });

    // Test 1: Allowlisted command type
    await shell.execute('echo "This should work"', 'testing allowlist');

    // Test 2: Blocklisted command type
    await shell.execute('rm some_file.txt', 'trying to delete');

    // Test 3: Another allowlisted command
    await shell.execute('dir', 'listing files');

    await shell.close();
}

main().catch(console.error);
