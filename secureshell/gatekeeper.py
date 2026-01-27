"""
Gatekeeper Orchestrator.
Manages the evaluation process using the configured LLM provider.
"""
from typing import Dict, Any, Optional
import structlog

from secureshell.models import GatekeeperResponse, RiskTier, GatekeeperDecision
from secureshell.providers.base import BaseLLMProvider

logger = structlog.get_logger()

class GatekeeperLLM:
    def __init__(self, provider: BaseLLMProvider):
        self.provider = provider
    
    async def assess(
        self,
        command: str,
        reasoning: str,
        risk_tier: RiskTier,
        context: Dict[str, Any]
    ) -> GatekeeperResponse:
        
        # If no reasoning provided for risky commands, auto-deny locally before hitting LLM
        # to save tokens and latency. 
        # (Though we force reasoning in tool definition, raw API usage might bypass it)
        if not reasoning and risk_tier in [RiskTier.YELLOW, RiskTier.RED]:
             return GatekeeperResponse(
                 decision=GatekeeperDecision.DENY,
                 explanation=f"Command '{command}' is classified as {risk_tier} but no reasoning was provided."
             )

        try:
            logger.info("gatekeeper_evaluating", command=command, risk=risk_tier)
            decision = await self.provider.evaluate_command(
                command, reasoning, risk_tier, context
            )
            logger.info("gatekeeper_decided", decision=decision.decision, reason=decision.explanation)
            return decision
        except Exception as e:
            logger.error("gatekeeper_failed", error=str(e))
            # Fail closed
            return GatekeeperResponse(
                decision=GatekeeperDecision.DENY,
                explanation=f"Gatekeeper error: {str(e)}"
            )
