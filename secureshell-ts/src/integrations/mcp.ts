/**
 * MCP Integration for SecureShell TypeScript SDK
 * 
 * Provides utility functions to create MCP-compatible tool definitions from SecureShell instances.
 */

import type { SecureShell } from '../SecureShell';

/**
 * Creates an MCP tool definition from a SecureShell instance
 * 
 * @param shell - SecureShell instance to wrap
 * @returns MCP tool definition compatible with @modelcontextprotocol/sdk
 */
export function createSecureShellMCPTool(shell: SecureShell) {
    return {
        name: 'execute_shell_command',
        description: 'Execute a shell command safely with AI gatekeeping. You MUST provide clear reasoning.',
        inputSchema: {
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
        },
        executor: async (args: { command: string; reasoning: string }) => {
            const result = await shell.execute(args.command, args.reasoning);
            return {
                content: [
                    {
                        type: 'text',
                        text: JSON.stringify({
                            success: result.success,
                            stdout: result.stdout,
                            stderr: result.stderr,
                            exit_code: result.exit_code,
                            gatekeeper_decision: result.gatekeeper_decision,
                            gatekeeper_reasoning: result.gatekeeper_reasoning,
                            risk_tier: result.risk_tier
                        }, null, 2)
                    }
                ]
            };
        }
    };
}
