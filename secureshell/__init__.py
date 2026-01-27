"""
SecureShell: A drop-in shell execution wrapper for LLM agents.
"""
from secureshell.core import SecureShell
from secureshell.config import SecureShellConfig
from secureshell.models import RiskTier, ExecutionResult

__version__ = "0.1.0"

__all__ = ["SecureShell", "SecureShellConfig", "RiskTier", "ExecutionResult"]
