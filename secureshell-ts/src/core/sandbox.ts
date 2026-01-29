/**
 * Sandbox Validator for SecureShell TypeScript SDK
 * Validates commands against path restrictions
 */

import * as path from 'path';
import * as fs from 'fs';

export class SandboxValidator {
    private allowedPaths: string[];
    private blockedPaths: string[];

    constructor(options?: { allowedPaths?: string[]; blockedPaths?: string[] }) {
        this.allowedPaths = options?.allowedPaths || [process.cwd()];
        this.blockedPaths = options?.blockedPaths || [];
    }

    /**
     * Validate if command is allowed within sandbox restrictions
     */
    validate(command: string, cwd: string = process.cwd()): { allowed: boolean; reason?: string } {
        // Extract file paths from command (basic heuristic)
        const paths = this.extractPaths(command);

        // Check if any path is in blocked paths
        for (const cmdPath of paths) {
            const resolvedPath = path.isAbsolute(cmdPath) ? cmdPath : path.resolve(cwd, cmdPath);

            // Check blocked paths
            for (const blocked of this.blockedPaths) {
                const resolvedBlocked = path.resolve(blocked);
                if (resolvedPath.startsWith(resolvedBlocked)) {
                    return {
                        allowed: false,
                        reason: `Path '${cmdPath}' is in blocked directory '${blocked}'`
                    };
                }
            }

            // Check if path is within allowed paths
            let inAllowedPath = false;
            for (const allowed of this.allowedPaths) {
                const resolvedAllowed = path.resolve(allowed);
                if (resolvedPath.startsWith(resolvedAllowed)) {
                    inAllowedPath = true;
                    break;
                }
            }

            if (!inAllowedPath && paths.length > 0) {
                return {
                    allowed: false,
                    reason: `Path '${cmdPath}' is outside allowed directories`
                };
            }
        }

        return { allowed: true };
    }

    /**
     * Extract potential file paths from command
     * This is a basic heuristic - not perfect but catches most cases
     */
    private extractPaths(command: string): string[] {
        const paths: string[] = [];

        // Look for common path patterns
        const pathPatterns = [
            // Absolute paths (Unix)
            /\/[^\s]+/g,
            // Absolute paths (Windows)
            /[A-Za-z]:\\[^\s]+/g,
            // Relative paths
            /\.\/[^\s]+/g,
            /\.\.[^\s]+/g
        ];

        for (const pattern of pathPatterns) {
            const matches = command.match(pattern);
            if (matches) {
                paths.push(...matches);
            }
        }

        // Clean up paths (remove quotes, trailing punctuation)
        return paths.map(p => p.replace(/['"]/g, '').replace(/[,;]$/, ''));
    }

    /**
     * Check if path exists and is within allowed zone
     */
    isPathAllowed(targetPath: string, cwd: string = process.cwd()): boolean {
        const resolvedPath = path.isAbsolute(targetPath) ? targetPath : path.resolve(cwd, targetPath);

        for (const allowed of this.allowedPaths) {
            const resolvedAllowed = path.resolve(allowed);
            if (resolvedPath.startsWith(resolvedAllowed)) {
                return true;
            }
        }

        return false;
    }
}
