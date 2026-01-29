/**
 * Command Executor for SecureShell TypeScript SDK
 * Executes shell commands with timeout and output capturing
 */

import { spawn } from 'child_process';
import * as os from 'os';

export interface ExecuteOptions {
    cwd?: string;
    timeout?: number; // in seconds
    maxOutputBytes?: number;
    shell?: boolean;
}

export interface ExecuteResult {
    success: boolean;
    stdout: string;
    stderr: string;
    exit_code: number;
    execution_time: number;
}

export class CommandExecutor {
    /**
     * Execute a shell command
     */
    async execute(command: string, options?: ExecuteOptions): Promise<ExecuteResult> {
        const startTime = Date.now();
        const cwd = options?.cwd || process.cwd();
        const timeout = (options?.timeout || 300) * 1000; // Convert to ms
        const maxOutputBytes = options?.maxOutputBytes || 1_000_000;

        return new Promise((resolve) => {
            let stdout = '';
            let stderr = '';
            let timedOut = false;

            // Determine shell to use
            const isWindows = os.platform() === 'win32';
            const shell = isWindows ? 'powershell.exe' : '/bin/sh';
            const shellArgs = isWindows ? ['-Command', command] : ['-c', command];

            const proc = spawn(shell, shellArgs, {
                cwd,
                shell: false,
                timeout: timeout
            });

            // Timeout handler
            const timeoutId = setTimeout(() => {
                timedOut = true;
                proc.kill('SIGTERM');

                resolve({
                    success: false,
                    stdout,
                    stderr: `Command timed out after ${timeout / 1000}s\n` + stderr,
                    exit_code: -1,
                    execution_time: Date.now() - startTime
                });
            }, timeout);

            // Capture stdout
            proc.stdout?.on('data', (data: Buffer) => {
                if (stdout.length < maxOutputBytes) {
                    stdout += data.toString();
                }
            });

            // Capture stderr
            proc.stderr?.on('data', (data: Buffer) => {
                if (stderr.length < maxOutputBytes) {
                    stderr += data.toString();
                }
            });

            // Handle completion
            proc.on('close', (code) => {
                if (!timedOut) {
                    clearTimeout(timeoutId);

                    resolve({
                        success: code === 0,
                        stdout,
                        stderr,
                        exit_code: code || 0,
                        execution_time: Date.now() - startTime
                    });
                }
            });

            // Handle errors
            proc.on('error', (error) => {
                clearTimeout(timeoutId);

                resolve({
                    success: false,
                    stdout,
                    stderr: error.message,
                    exit_code: -1,
                    execution_time: Date.now() - startTime
                });
            });
        });
    }
}
