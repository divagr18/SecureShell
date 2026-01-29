/**
 * Security Templates for SecureShell
 * Matching Python implementation
 */

import { SecurityTemplate } from '../models/types';

export const TEMPLATES: Record<string, SecurityTemplate> = {
    development: {
        name: 'development',
        description: 'Permissive template for local development',
        allowlist: [
            'ls', 'pwd', 'echo', 'cat', 'grep', 'find',
            'git status', 'git log', 'git diff',
            'npm install', 'npm run', 'python', 'node'
        ],
        blocklist: [
            'rm -rf /', 'dd', 'mkfs', 'format',
            ':(){ :|:& };:',  // Fork bombs
            'curl | sh', 'wget | sh'
        ],
        auto_approve_green: true
    },

    production: {
        name: 'production',
        description: 'Strict security for production environments',
        allowlist: [
            'ls', 'pwd', 'echo', 'cat',
            'git pull', 'git status'
        ],
        blocklist: [
            'rm', 'mv', 'dd', 'mkfs', 'format',
            'sudo', 'su',
            'curl | sh', 'wget | sh',
            ':(){ :|:& };:'
        ],
        auto_approve_green: false
    },

    paranoid: {
        name: 'paranoid',
        description: 'Maximum security - gatekeeper reviews everything',
        allowlist: [],
        blocklist: [
            'rm', 'mv', 'dd', 'mkfs', 'format',
            'sudo', 'su', 'chmod', 'chown',
            'curl', 'wget',
            ':(){ :|:& };:',
            '>', '|'  // Redirects and pipes
        ],
        auto_approve_green: false
    },

    ci_cd: {
        name: 'ci_cd',
        description: 'Balanced template for CI/CD pipelines',
        allowlist: [
            'ls', 'pwd', 'echo', 'cat', 'grep',
            'git', 'npm', 'yarn', 'pnpm',
            'docker build', 'docker push',
            'kubectl apply', 'helm install'
        ],
        blocklist: [
            'rm -rf /', 'dd', 'mkfs', 'format',
            ':(){ :|:& };:',
            'curl | sh', 'wget | sh'
        ],
        auto_approve_green: true
    }
};

/**
 * Get a security template by name
 */
export function getTemplate(name: string): SecurityTemplate {
    const template = TEMPLATES[name];
    if (!template) {
        throw new Error(`Unknown template: ${name}. Available: ${Object.keys(TEMPLATES).join(', ')}`);
    }
    return template;
}

/**
 * List all available templates
 */
export function listTemplates(): string[] {
    return Object.keys(TEMPLATES);
}
