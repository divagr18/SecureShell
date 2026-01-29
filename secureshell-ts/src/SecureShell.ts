/**
 * Main SecureShell class for TypeScript SDK
 * Drop-in replacement for shell execution with AI gatekeeping
 */

import * as os from 'os';
import * as path from 'path';
import { BaseLLMProvider } from './providers/base';
import { OpenAIProvider } from './providers/openai';
import { RiskClassifier } from './core/risk_classifier';
import { SandboxValidator } from './core/sandbox';
import { CommandExecutor } from './core/executor';
import { AuditLogger } from './core/audit';
import { Gatekeeper } from './core/gatekeeper';
import { loadConfig } from './config/loader';
import { getTemplate } from './config/templates';
import {
    ExecutionResult,
    RiskTier,
    GatekeeperDecision,
    SecureShellConfig,
    SecurityContext
} from './models/types';

export class SecureShell {
    private riskClassifier: RiskClassifier;
    private sandbox: SandboxValidator;
    private executor: CommandExecutor;
    private auditLogger: AuditLogger;
    private gatekeeper?: Gatekeeper;
    public config: SecureShellConfig;
    private osInfo: string;

    constructor(options?: {
        provider?: BaseLLMProvider;
        config?: SecureShellConfig;
        template?: string;
        allowedPaths?: string[];
        blockedPaths?: string[];
        osInfo?: string;
    }) {
        // Load configuration
        this.config = options?.config || loadConfig();

        // Apply security template if specified
        if (options?.template) {
            const tmpl = getTemplate(options.template);
            console.log(`[SecureShell] Loading template: ${options.template}`);

            if (!this.config.allowlist || this.config.allowlist.length === 0) {
                this.config.allowlist = tmpl.allowlist;
            }
            if (!this.config.blocklist || this.config.blocklist.length === 0) {
                this.config.blocklist = tmpl.blocklist;
            }
        }

        // Initialize components
        this.riskClassifier = new RiskClassifier();

        const allowedPaths = options?.allowedPaths || [process.cwd()];
        const blockedPaths = options?.blockedPaths;

        this.sandbox = new SandboxValidator({ allowedPaths, blockedPaths });
        this.executor = new CommandExecutor();
        this.auditLogger = new AuditLogger({
            logPath: this.config.auditLogPath,
            maxBytes: 10 * 1024 * 1024
        });

        // Setup provider and gatekeeper
        if (options?.provider) {
            this.gatekeeper = new Gatekeeper(options.provider);
        } else {
            // Auto-configure provider based on config
            const provider = this.autoConfigureProvider();
            if (provider) {
                this.gatekeeper = new Gatekeeper(provider);
            }
        }

        // OS info - auto-detect if not provided
        this.osInfo = options?.osInfo || this.config.osInfo || this.detectOS();

        if (this.config.debugMode) {
            console.log('[SecureShell] Initialized', {
                osInfo: this.osInfo,
                hasGatekeeper: !!this.gatekeeper,
                allowlist: this.config.allowlist,
                blocklist: this.config.blocklist
            });
        }
    }

    /**
     * Detect OS in a friendly format
     */
    private detectOS(): string {
        const platform = os.platform();
        const release = os.release();

        switch (platform) {
            case 'win32':
                return 'Windows';
            case 'darwin':
                return 'macOS';
            case 'linux':
                return 'Linux';
            default:
                return `${platform} ${release}`;
        }
    }

    /**
     * Auto-configure provider based on environment variables
     */
    private autoConfigureProvider(): BaseLLMProvider | null {
        if (this.config.provider === 'openai' && this.config.openaiApiKey) {
            return new OpenAIProvider({
                apiKey: this.config.openaiApiKey,
                model: 'gpt-4.1-mini'
            });
        }

        // Add other providers as needed
        console.warn('[SecureShell] No provider configured. Gatekeeper disabled.');
        return null;
    }

    /**
     * Get the detected or configured OS name
     */
    getOSInfo(): string {
        return this.osInfo;
    }

    /**
     * Execute a command securely with gatekeeper evaluation
     */
    async execute(command: string, reasoning: string = '', context?: Partial<SecurityContext>): Promise<ExecutionResult> {
        const fullContext: SecurityContext = {
            user: os.userInfo().username,
            cwd: process.cwd(),
            env_vars: process.env as Record<string, string>,
            os: this.osInfo,
            ...context
        };

        console.log(`[SecureShell] Executing: ${command}`);

        const startTime = Date.now();

        // 1. Sandbox Validation
        const sandboxResult = this.sandbox.validate(command, fullContext.cwd);
        if (!sandboxResult.allowed) {
            const result = this.createBlockedResult(
                command,
                'Sandbox Violation',
                sandboxResult.reason || 'Path access denied',
                RiskTier.BLOCKED
            );
            await this.auditLogger.logExecution(command, reasoning, fullContext, result);
            if (this.config.debugMode) {
                this.printDebugSummary(command, reasoning, RiskTier.BLOCKED, result);
            }
            return result;
        }

        // 2. Config Policy Check (Blocklist)
        const commandType = command.split(/\s+/)[0];
        for (const pattern of this.config.blocklist || []) {
            if (commandType === pattern || command.startsWith(pattern)) {
                const result = this.createBlockedResult(
                    command,
                    'Config Blocked',
                    `Command matches blocklist pattern: ${pattern}`,
                    RiskTier.BLOCKED
                );
                await this.auditLogger.logExecution(command, reasoning, fullContext, result);
                if (this.config.debugMode) {
                    this.printDebugSummary(command, reasoning, RiskTier.BLOCKED, result);
                }
                return result;
            }
        }

        // 3. Check Allowlist (Bypass everything)
        for (const pattern of this.config.allowlist || []) {
            if (commandType === pattern || command.startsWith(pattern)) {
                console.log(`[SecureShell] Command allowlisted, bypassing gatekeeper`);
                return await this.executeCommand(command, fullContext, reasoning, RiskTier.GREEN);
            }
        }

        // 4. Risk Classification
        const riskTier = this.riskClassifier.classify(command, this.config);

        if (this.config.debugMode) {
            console.log(`[SecureShell] Risk Tier: ${riskTier}`);
        }

        // 5. Auto-block BLOCKED tier
        if (riskTier === RiskTier.BLOCKED) {
            const result = this.createBlockedResult(
                command,
                'High Risk Blocked',
                'Command pattern is blocked by risk classifier',
                riskTier
            );
            await this.auditLogger.logExecution(command, reasoning, fullContext, result);
            if (this.config.debugMode) {
                this.printDebugSummary(command, reasoning, riskTier, result);
            }
            return result;
        }

        // 6. Gatekeeper Evaluation
        if (!this.gatekeeper) {
            // No gatekeeper - execute directly for GREEN, block for YELLOW/RED
            if (riskTier === RiskTier.GREEN) {
                return await this.executeCommand(command, fullContext, reasoning, riskTier);
            } else {
                const result = this.createBlockedResult(
                    command,
                    'No Gatekeeper',
                    'Risky command but no gatekeeper configured',
                    riskTier
                );
                await this.auditLogger.logExecution(command, reasoning, fullContext, result);
                if (this.config.debugMode) {
                    this.printDebugSummary(command, reasoning, riskTier, result);
                }
                return result;
            }
        }

        const gatekeeperResponse = await this.gatekeeper.assess(command, reasoning, riskTier, fullContext);

        // 7. Handle Gatekeeper Decision
        if (gatekeeperResponse.decision === GatekeeperDecision.ALLOW) {
            return await this.executeCommand(command, fullContext, reasoning, riskTier, gatekeeperResponse.reasoning);
        } else if (gatekeeperResponse.decision === GatekeeperDecision.CHALLENGE) {
            const result: ExecutionResult = {
                success: false,
                stdout: '',
                stderr: 'Challenge required',
                exit_code: -1,
                execution_time: Date.now() - startTime,
                command,
                risk_tier: riskTier,
                gatekeeper_decision: gatekeeperResponse.decision,
                gatekeeper_reasoning: gatekeeperResponse.reasoning,
                required_clarification: gatekeeperResponse.required_clarification
            };
            await this.auditLogger.logExecution(command, reasoning, fullContext, result);
            if (this.config.debugMode) {
                this.printDebugSummary(command, reasoning, riskTier, result);
            }
            return result;
        } else {
            // DENY
            const result = this.createBlockedResult(
                command,
                'Gatekeeper Denied',
                gatekeeperResponse.reasoning,
                riskTier,
                gatekeeperResponse.decision
            );
            await this.auditLogger.logExecution(command, reasoning, fullContext, result);

            if (this.config.debugMode) {
                this.printDebugSummary(command, reasoning, riskTier, result);
            }

            return result;
        }
    }

    /**
     * Actually execute the command
     */
    private async executeCommand(
        command: string,
        context: SecurityContext,
        reasoning: string,
        riskTier: RiskTier,
        gatekeeperReasoning?: string
    ): Promise<ExecutionResult> {
        const execResult = await this.executor.execute(command, {
            cwd: context.cwd,
            timeout: this.config.defaultTimeoutSeconds,
            maxOutputBytes: this.config.maxOutputBytes
        });

        const result: ExecutionResult = {
            ...execResult,
            command,
            risk_tier: riskTier,
            gatekeeper_decision: gatekeeperReasoning ? GatekeeperDecision.ALLOW : undefined,
            gatekeeper_reasoning: gatekeeperReasoning
        };

        await this.auditLogger.logExecution(command, reasoning, context, result);

        if (this.config.debugMode) {
            this.printDebugSummary(command, reasoning, riskTier, result);
        }

        return result;
    }

    /**
     * Create a blocked execution result
     */
    private createBlockedResult(
        command: string,
        reason: string,
        details: string,
        riskTier: RiskTier,
        decision?: GatekeeperDecision
    ): ExecutionResult {
        return {
            success: false,
            stdout: '',
            stderr: `❌ ${reason}: ${details}`,
            exit_code: -1,
            execution_time: 0,
            command,
            risk_tier: riskTier,
            gatekeeper_decision: decision || GatekeeperDecision.DENY,
            gatekeeper_reasoning: details
        };
    }

    /**
     * Print a user-friendly debug summary (similar to Python SDK)
     */
    private printDebugSummary(command: string, reasoning: string, riskTier: RiskTier, result: ExecutionResult): void {
        const border = '='.repeat(60);
        console.log('\n' + border);
        console.log('[SecureShell Debug]');
        console.log(border);

        // Determine decision status
        let decision: string;
        if (result.gatekeeper_decision === GatekeeperDecision.DENY || !result.success && result.stderr.includes('❌')) {
            decision = '[BLOCKED]';
        } else if (result.success) {
            decision = '[ALLOWED]';
        } else {
            decision = '[ALLOWED (execution failed)]';
        }

        // Display key information
        console.log(`${'Command'.padEnd(20)}: ${command}`);
        console.log(`${'Reasoning'.padEnd(20)}: ${reasoning}`);
        console.log(`${'Risk Tier'.padEnd(20)}: ${riskTier}`);
        console.log(`${'Decision'.padEnd(20)}: ${decision}`);

        if (result.success) {
            const output = result.stdout.trim();
            const displayOutput = output.length > 200 ? output.substring(0, 200) + '...' : output;
            console.log(`${'Output'.padEnd(20)}: ${displayOutput}`);
            if (result.stderr) {
                const stderrTrimmed = result.stderr.trim();
                if (stderrTrimmed.length > 0) {
                    const displayStderr = stderrTrimmed.length > 100 ? stderrTrimmed.substring(0, 100) + '...' : stderrTrimmed;
                    console.log(`${'Stderr'.padEnd(20)}: ${displayStderr}`);
                }
            }
        } else {
            if (result.stderr) {
                const errorMsg = result.stderr.trim();
                const displayError = errorMsg.length > 200 ? errorMsg.substring(0, 200) + '...' : errorMsg;
                console.log(`${'Error'.padEnd(20)}: ${displayError}`);
            }
            if (result.gatekeeper_reasoning) {
                console.log(`${'Gatekeeper'.padEnd(20)}: ${result.gatekeeper_decision}: ${result.gatekeeper_reasoning}`);
            }
        }

        console.log(border + '\n');
    }

    /**
     * Flush audit logs
     */
    async close(): Promise<void> {
        await this.auditLogger.flush();
    }
}
