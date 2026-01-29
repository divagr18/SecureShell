/**
 * Audit Logger for SecureShell TypeScript SDK
 * Async logging with JSONL format
 */

import * as fs from 'fs';
import * as fsPromises from 'fs/promises';
import * as path from 'path';
import { AuditLogEntry, SecurityContext, ExecutionResult } from '../models/types';

export class AuditLogger {
    private logPath: string;
    private maxBytes: number;
    private backupCount: number;
    private logQueue: AuditLogEntry[] = [];
    private isProcessing: boolean = false;

    constructor(options?: {
        logPath?: string;
        maxBytes?: number;
        backupCount?: number;
    }) {
        this.logPath = options?.logPath || 'secureshell_audit.jsonl';
        this.maxBytes = options?.maxBytes || 10 * 1024 * 1024; // 10MB
        this.backupCount = options?.backupCount || 5;
    }

    /**
     * Log command execution to audit trail
     */
    async logExecution(
        command: string,
        reasoning: string,
        context: SecurityContext,
        result: Partial<ExecutionResult>
    ): Promise<void> {
        const entry: AuditLogEntry = {
            timestamp: new Date().toISOString(),
            command,
            risk_tier: result.risk_tier!,
            gatekeeper_decision: result.gatekeeper_decision,
            gatekeeper_reasoning: result.gatekeeper_reasoning,
            execution_result: result.success !== undefined ? {
                success: result.success,
                exit_code: result.exit_code || 0,
                execution_time: result.execution_time || 0
            } : undefined,
            context
        };

        this.logQueue.push(entry);

        // Process queue asynchronously
        if (!this.isProcessing) {
            this.processQueue();
        }
    }

    /**
     * Process log entries from queue
     */
    private async processQueue(): Promise<void> {
        if (this.logQueue.length === 0 || this.isProcessing) {
            return;
        }

        this.isProcessing = true;

        try {
            // Get batch of entries
            const entries = this.logQueue.splice(0, 50);

            // Check if rotation needed
            await this.rotateIfNeeded();

            // Write batch to file
            const lines = entries.map(entry => JSON.stringify(entry) + '\n').join('');
            await fsPromises.appendFile(this.logPath, lines, 'utf8');

        } catch (error) {
            console.error('Audit log write failed:', error);
        } finally {
            this.isProcessing = false;

            // Process remaining items
            if (this.logQueue.length > 0) {
                setImmediate(() => this.processQueue());
            }
        }
    }

    /**
     * Rotate log file if it exceeds max size
     */
    private async rotateIfNeeded(): Promise<void> {
        try {
            if (!fs.existsSync(this.logPath)) {
                return;
            }

            const stats = await fsPromises.stat(this.logPath);

            if (stats.size >= this.maxBytes) {
                // Rotate existing backups
                for (let i = this.backupCount - 1; i > 0; i--) {
                    const oldFile = `${this.logPath}.${i}`;
                    const newFile = `${this.logPath}.${i + 1}`;

                    if (fs.existsSync(oldFile)) {
                        if (fs.existsSync(newFile)) {
                            await fsPromises.unlink(newFile);
                        }
                        await fsPromises.rename(oldFile, newFile);
                    }
                }

                // Move current to .1
                const backup = `${this.logPath}.1`;
                if (fs.existsSync(backup)) {
                    await fsPromises.unlink(backup);
                }
                await fsPromises.rename(this.logPath, backup);
            }
        } catch (error) {
            console.error('Audit log rotation failed:', error);
        }
    }

    /**
     * Flush any remaining log entries
     */
    async flush(): Promise<void> {
        while (this.logQueue.length > 0 || this.isProcessing) {
            await new Promise(resolve => setTimeout(resolve, 100));
        }
    }
}
