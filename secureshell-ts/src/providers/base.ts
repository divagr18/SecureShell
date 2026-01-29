/**
 * Base Provider Interface for SecureShell TypeScript SDK
 */

import { GatekeeperResponse, RiskTier, SecurityContext } from '../models/types';

export abstract class BaseLLMProvider {
    /**
     * Evaluate a command and return a structured gatekeeper decision
     */
    abstract evaluateCommand(
        command: string,
        reasoning: string,
        riskTier: RiskTier,
        context: SecurityContext
    ): Promise<GatekeeperResponse>;

    /**
     * Get provider name
     */
    abstract get providerName(): string;
}
