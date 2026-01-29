import { z } from 'zod';
import { DynamicStructuredTool } from '@langchain/core/tools';
import type { SecureShell } from '../SecureShell';

/**
 * Schema for the SecureShell tool input
 */
const executeCommandSchema = z.object({
    command: z.string().describe('The shell command to execute'),
    reasoning: z.string().describe('Detailed explanation of why this command is necessary and what it will accomplish'),
});

// Explicit input type inferred from schema for convenience in the func implementation
type ExecuteCommandInput = z.infer<typeof executeCommandSchema>;

/**
 * Creates a LangChain tool from a SecureShell instance
 *
 * Note: cast to `any` is intentional to avoid TS's "Type instantiation is excessively deep" error
 * caused by heavy generic inference inside DynamicStructuredTool.
 */
export function createSecureShellTool(shell: SecureShell): any {
    // keep the implementation of func explicitly typed to help editor/reader
    const func = async (input: ExecuteCommandInput): Promise<string> => {
        const { command, reasoning } = input;
        const result = await shell.execute(command, reasoning);

        if (result.success) {
            return JSON.stringify(
                {
                    success: true,
                    stdout: result.stdout,
                    stderr: result.stderr,
                    execution_time: result.execution_time,
                },
                null,
                2
            );
        } else {
            return JSON.stringify(
                {
                    success: false,
                    error: result.stderr,
                    gatekeeper_decision: result.gatekeeper_decision,
                    gatekeeper_reasoning: result.gatekeeper_reasoning,
                },
                null,
                2
            );
        }
    };

    // Build spec as a plain object and cast to any to short-circuit heavy type inference
    const toolSpec: any = {
        name: 'execute_shell_command',
        description:
            'Execute a shell command safely with AI-powered gatekeeper validation. You MUST provide clear reasoning for why you need to run this command.',
        schema: executeCommandSchema,
        func,
    };

    // Construct and return the tool (cast to any to avoid TS recursion limits)
    return new (DynamicStructuredTool as any)(toolSpec);
}
