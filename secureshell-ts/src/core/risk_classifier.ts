/**
 * Risk Classification Engine for SecureShell TypeScript SDK
 * Determines the risk tier of a command based on regex patterns
 */

import { RiskTier, SecureShellConfig } from '../models/types';

interface RiskPattern {
    pattern: RegExp;
    tier: RiskTier;
    description: string;
}

export class RiskClassifier {
    private rules: RiskPattern[] = [];

    constructor(customRules?: Partial<Record<RiskTier, string[]>>) {
        this.initializeDefaults();
        if (customRules) {
            this.addCustomRules(customRules);
        }
    }

    private initializeDefaults(): void {
        // BLOCKED: Fork bombs, system destruction, known malicious patterns
        this.addRule(/:\(\)\{\s*:\|\s*:\s*&\s*\}\s*;/, RiskTier.BLOCKED, 'Fork bomb');
        this.addRule(/mkfs/, RiskTier.BLOCKED, 'Filesystem formatting');
        this.addRule(/dd\s+if=/, RiskTier.BLOCKED, 'Low-level disk writing');
        this.addRule(/> \/dev\/sd[a-z]/, RiskTier.BLOCKED, 'Raw device writing');

        // RED: High impact, destructive, permission changes
        this.addRule(/rm\s+.*(-r|-f|--recursive|--force)/, RiskTier.RED, 'Recursive/forced deletion');
        this.addRule(/chmod/, RiskTier.RED, 'Permission modification');
        this.addRule(/chown/, RiskTier.RED, 'Ownership modification');
        this.addRule(/sudo/, RiskTier.RED, 'Privilege escalation');
        this.addRule(/git\s+push\s+.*(--force|-f)/, RiskTier.RED, 'Force push');
        this.addRule(/systemctl\s+(stop|disable|mask)/, RiskTier.RED, 'Service modification');

        // YELLOW: Network, external mutations, non-recursive deletion
        this.addRule(/rm\s+[^-]/, RiskTier.YELLOW, 'File deletion');
        this.addRule(/curl/, RiskTier.YELLOW, 'Network request (curl)');
        this.addRule(/wget/, RiskTier.YELLOW, 'Network request (wget)');
        this.addRule(/git\s+push/, RiskTier.YELLOW, 'Git push');
        this.addRule(/ssh/, RiskTier.YELLOW, 'SSH connection');
        this.addRule(/npm\s+(publish|i|install)/, RiskTier.YELLOW, 'Package installation/publishing');
        this.addRule(/pip\s+install/, RiskTier.YELLOW, 'Package installation');

        // GREEN: Specific safe read-only commands
        this.addRule(/^ls(\s|$)/, RiskTier.GREEN, 'List directory');
        this.addRule(/^dir(\s|$)/, RiskTier.GREEN, 'List directory (Windows)');
        this.addRule(/^pwd(\s|$)/, RiskTier.GREEN, 'Print working directory');
        this.addRule(/^echo(\s|$)/, RiskTier.GREEN, 'Echo');
        this.addRule(/^cat(\s|$)/, RiskTier.GREEN, 'Read file');
        this.addRule(/^type(\s|$)/, RiskTier.GREEN, 'Read file (Windows)');
        this.addRule(/^git\s+status/, RiskTier.GREEN, 'Git status');
        this.addRule(/^git\s+log/, RiskTier.GREEN, 'Git log');
        this.addRule(/^grep/, RiskTier.GREEN, 'Grep search');
        this.addRule(/^find/, RiskTier.GREEN, 'Find files');
    }

    private addRule(pattern: RegExp, tier: RiskTier, description: string): void {
        this.rules.push({ pattern, tier, description });
    }

    private addCustomRules(customRules: Partial<Record<RiskTier, string[]>>): void {
        for (const [tier, patterns] of Object.entries(customRules)) {
            if (patterns && Array.isArray(patterns)) {
                for (const patternStr of patterns) {
                    try {
                        const pattern = new RegExp(patternStr, 'i');
                        this.addRule(pattern, tier as RiskTier, 'Custom rule');
                    } catch (error) {
                        console.error(`Invalid risk pattern: ${patternStr}`, error);
                    }
                }
            }
        }
    }

    /**
     * Classify command into risk tier
     * 
     * Priority:
     * 1. Blocklist (Exact Prefix) -> BLOCKED
     * 2. Allowlist (Exact Prefix) -> GREEN
     * 3. Regex Patterns -> Matched Tier
     * 4. Default -> YELLOW
     */
    classify(command: string, config?: SecureShellConfig): RiskTier {
        // 1. Check Blocklist (highest priority)
        if (config?.blocklist) {
            for (const blocked of config.blocklist) {
                if (command.startsWith(blocked)) {
                    return RiskTier.BLOCKED;
                }
            }
        }

        // 2. Check Allowlist
        if (config?.allowlist) {
            for (const allowed of config.allowlist) {
                if (command.startsWith(allowed)) {
                    return RiskTier.GREEN;
                }
            }
        }

        // 3. Regex Pattern Matching
        const tierSeverity: Record<RiskTier, number> = {
            [RiskTier.BLOCKED]: 4,
            [RiskTier.RED]: 3,
            [RiskTier.YELLOW]: 2,
            [RiskTier.GREEN]: 1
        };

        let highestRisk = RiskTier.GREEN;
        let matchedRule: RiskPattern | null = null;

        for (const rule of this.rules) {
            if (rule.pattern.test(command)) {
                if (tierSeverity[rule.tier] > tierSeverity[highestRisk]) {
                    highestRisk = rule.tier;
                    matchedRule = rule;
                }
            }
        }

        // 4. Default to YELLOW if no explicit GREEN match found
        if (highestRisk === RiskTier.GREEN && matchedRule === null) {
            return RiskTier.YELLOW;
        }

        return highestRisk;
    }
}
