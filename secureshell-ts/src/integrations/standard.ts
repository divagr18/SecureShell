/**
 * Standard Integration for SecureShell TypeScript SDK
 * 
 * Provides utility functions to create standard OpenAI-compatible tool definitions
 * which function with OpenAI, Anthropic (via conversion), Gemini, and others.
 */

import type { SecureShell } from '../SecureShell';

/**
 * Creates a standard JSON Schema tool definition from a SecureShell instance
 * Compatible with OpenAI function calling API
 * 
 * @param shell - SecureShell instance to wrap
 * @returns JSON Schema tool definition
 */
export function createSecureShellStandardTool(shell: SecureShell) {
    const toolDefinition = {
        type: 'function',
        function: {
            name: 'execute_shell_command',
            description: 'Execute a shell command safely with AI gatekeeping. You MUST provide clear reasoning.',
            parameters: {
                type: 'object',
                properties: {
                    command: {
                        type: 'string',
                        description: 'The shell command to execute'
                    },
                    reasoning: {
                        type: 'string',
                        description: 'Detailed explanation of why this command is necessary (minimum 10 characters)'
                    }
                },
                required: ['command', 'reasoning']
            }
        }
    };

    const executor = async (args: { command: string; reasoning: string } | string) => {
        let parsedArgs: { command: string; reasoning: string };

        if (typeof args === 'string') {
            try {
                parsedArgs = JSON.parse(args);
            } catch (e) {
                return JSON.stringify({
                    success: false,
                    error: 'Invalid JSON arguments'
                });
            }
        } else {
            parsedArgs = args;
        }

        const result = await shell.execute(parsedArgs.command, parsedArgs.reasoning);

        return JSON.stringify({
            success: result.success,
            stdout: result.stdout,
            stderr: result.stderr,
            exit_code: result.exit_code,
            gatekeeper_decision: result.gatekeeper_decision,
            gatekeeper_reasoning: result.gatekeeper_reasoning,
            risk_tier: result.risk_tier
        }, null, 2);
    };

    return {
        definition: toolDefinition,
        executor: executor
    };
}
