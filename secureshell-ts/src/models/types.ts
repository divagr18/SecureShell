/**
 * Core type definitions and enums for SecureShell TypeScript SDK
 */

/**
 * Risk tier classification for commands
 */
export enum RiskTier {
    GREEN = "GREEN",     // Auto-allow (ls, pwd, echo)
    YELLOW = "YELLOW",   // Gatekeeper review (rm, git push)
    RED = "RED",         // Strict review (rm -rf, sudo)
    BLOCKED = "BLOCKED"  // Always deny (dd, mkfs, fork bombs)
}

/**
 * Gatekeeper decision types
 */
export enum GatekeeperDecision {
    ALLOW = "ALLOW",
    DENY = "DENY",
    CHALLENGE = "CHALLENGE"
}

/**
 * Gatekeeper response from LLM provider
 */
export interface GatekeeperResponse {
    decision: GatekeeperDecision;
    reasoning: string;
    required_clarification?: string;  // Used when decision is CHALLENGE
}

/**
 * Command execution result
 */
export interface ExecutionResult {
    success: boolean;
    stdout: string;
    stderr: string;
    exit_code: number;
    execution_time: number;
    command: string;
    risk_tier: RiskTier;
    gatekeeper_decision?: GatekeeperDecision;
    gatekeeper_reasoning?: string;
    required_clarification?: string;
}

/**
 * Security context for gatekeeper evaluation
 */
export interface SecurityContext {
    user: string;
    cwd: string;
    env_vars: Record<string, string>;
    os: string;
    [key: string]: any;
}

/**
 * Audit log entry
 */
export interface AuditLogEntry {
    timestamp: string;
    command: string;
    risk_tier: RiskTier;
    gatekeeper_decision?: GatekeeperDecision;
    gatekeeper_reasoning?: string;
    execution_result?: {
        success: boolean;
        exit_code: number;
        execution_time: number;
    };
    context: SecurityContext;
}

/**
 * Configuration options for SecureShell
 */
export interface SecureShellConfig {
    // Core Settings
    appName?: string;
    environment?: string;
    debugMode?: boolean;

    // Provider Settings
    provider?: string;
    openaiApiKey?: string;
    anthropicApiKey?: string;
    geminiApiKey?: string;
    groqApiKey?: string;
    deepseekApiKey?: string;

    // Execution Settings
    defaultTimeoutSeconds?: number;
    maxOutputBytes?: number;

    // Audit Settings
    auditLogPath?: string;
    auditQueueSize?: number;

    // Allowlist/Blocklist
    allowlist?: string[];
    blocklist?: string[];

    // OS Information
    osInfo?: string;
}

/**
 * Security template definition
 */
export interface SecurityTemplate {
    name: string;
    description: string;
    allowlist: string[];
    blocklist: string[];
    auto_approve_green?: boolean;
    challenge_threshold?: number;
}
