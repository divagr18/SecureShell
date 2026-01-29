/**
 * Gatekeeper Orchestrator for SecureShell TypeScript SDK
 */

import { BaseLLMProvider } from '../providers/base';
import { GatekeeperResponse, GatekeeperDecision, RiskTier, SecurityContext } from '../models/types';

export class Gatekeeper {
    private provider: BaseLLMProvider;

    constructor(provider: BaseLLMProvider) {
        this.provider = provider;
    }

    /**
     * Assess a command using the LLM provider
     */
    async assess(
        command: string,
        reasoning: string,
        riskTier: RiskTier,
        context: SecurityContext
    ): Promise<GatekeeperResponse> {
        // Auto-deny risky commands without reasoning
        if (!reasoning && (riskTier === RiskTier.YELLOW || riskTier === RiskTier.RED)) {
            return {
                decision: GatekeeperDecision.DENY,
                reasoning: `Command '${command}' is classified as ${riskTier} but no reasoning was provided.`
            };
        }

        try {
            console.log(`[Gatekeeper] Evaluating command: ${command} (Risk: ${riskTier})`);
            const decision = await this.provider.evaluateCommand(command, reasoning, riskTier, context);
            console.log(`[Gatekeeper] Decision: ${decision.decision} - ${decision.reasoning}`);
            return decision;
        } catch (error) {
            console.error('[Gatekeeper] Error:', error);
            // Fail closed
            return {
                decision: GatekeeperDecision.DENY,
                reasoning: `Gatekeeper error: ${error instanceof Error ? error.message : String(error)}`
            };
        }
    }
}
