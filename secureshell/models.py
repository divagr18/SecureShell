"""
Pydantic models for SecureShell.
"""
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class RiskTier(str, Enum):
    """Command risk classification tiers."""
    GREEN = "GREEN"      # Auto-allow (ls, pwd, echo)
    YELLOW = "YELLOW"    # Gatekeeper review (rm, git push)
    RED = "RED"          # Strict review (rm -rf, sudo)
    BLOCKED = "BLOCKED"  # Always deny (dd, mkfs, fork bombs)


class GatekeeperDecision(str, Enum):
    """Gatekeeper decision types."""
    ALLOW = "ALLOW"
    DENY = "DENY"


class GatekeeperResponse(BaseModel):
    """Response from gatekeeper LLM evaluation."""
    decision: GatekeeperDecision
    explanation: str
    suggested_alternative: Optional[str] = None
    required_clarification: Optional[str] = None


class CheckResult(BaseModel):
    """Result of a validation check."""
    passed: bool
    reason: Optional[str] = None


class ExecutionResult(BaseModel):
    """Result of command execution."""
    success: bool
    stdout: str = ""
    stderr: str = ""
    denial_reason: Optional[str] = None
    risk_tier: Optional[RiskTier] = None
    gatekeeper_response: Optional[GatekeeperResponse] = None
