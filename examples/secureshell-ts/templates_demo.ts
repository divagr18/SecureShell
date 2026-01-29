/**
 * Security Templates Demo for SecureShell TypeScript
 * 
 * Demonstrates all 4 pre-built security templates.
 * 
 * Usage:
 *   npx tsx examples/secureshell-ts/features/templates_demo.ts
 */

import { SecureShell, listTemplates } from '@secureshell/ts';

async function testTemplate(templateName: string) {
    console.log(`\n${'='.repeat(60)}`);
    console.log(`Testing Template: ${templateName.toUpperCase()}`);
    console.log(`${'='.repeat(60)}\n`);

    const shell = new SecureShell({
        template: templateName
        // No provider = testing config policies only
    });

    console.log('Allowlist:', shell.config.allowlist);
    console.log('Blocklist:', shell.config.blocklist, '\n');

    // Test commands
    const commands: Array<[string, string]> = [
        ['echo "Hello from SecureShell!"', 'greeting'],
        ['ls -la', 'list files'],
        ['npm install', 'install package'],
        ['rm test.txt', 'delete file'],
        ['git status', 'check git status']
    ];

    for (const [cmd, reason] of commands) {
        const result = await shell.execute(cmd, reason);
        const status = result.success ? '✅ ALLOWED' : '❌ BLOCKED';
        const details = result.success ? 'Executed' : result.stderr;
        console.log(`${status.padEnd(12)} | ${cmd.padEnd(35)} | ${details}`);
    }

    await shell.close();
}

async function main() {
    console.log('🚀 SecureShell Security Templates Demo\n');
    console.log('This demo shows how different templates handle the same commands.\n');

    // Test all templates
    const templates = ['paranoid', 'development', 'production', 'ci_cd'];

    for (const template of templates) {
        await testTemplate(template);
    }

    // Summary
    console.log(`\n${'='.repeat(60)}`);
    console.log('Summary');
    console.log(`${'='.repeat(60)}`);
    console.log(`
    🔒 paranoid:     Most restrictive - max security
    🛠️  development:  Most permissive - developer friendly
    🏭 production:   Balanced - production safe
    🚀 ci_cd:        Build tool focused - CI/CD optimized
    
    Choose the template that matches your use case!
    See examples/SECURITY_TEMPLATES.md for full documentation.
  `);
}

main().catch(console.error);
