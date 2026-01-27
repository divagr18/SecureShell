"""
Abstract Base Class for LLM Providers.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

from secureshell.models import GatekeeperResponse, RiskTier

class BaseLLMProvider(ABC):
    """
    Interface that all LLM providers must implement.
    """
    
    @abstractmethod
    async def evaluate_command(
        self, 
        command: str, 
        reasoning: str, 
        risk_tier: RiskTier,
        context: Dict[str, Any]
    ) -> GatekeeperResponse:
        """
        Evaluate a command and return a structured decision.
        """
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the name of the provider (e.g. 'openai', 'anthropic')."""
        pass
