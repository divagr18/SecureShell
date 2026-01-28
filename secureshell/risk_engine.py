"""
Risk classification engine for SecureShell.
Determines the risk tier of a command based on regex patterns and heuristics.
"""
import re
from typing import List, Pattern, Dict
from pydantic import BaseModel
import structlog

from secureshell.models import RiskTier

logger = structlog.get_logger()

class RiskPattern(BaseModel):
    pattern: Pattern
    tier: RiskTier
    description: str

class RiskClassifier:
    """
    Classifies shell commands into risk tiers (GREEN, YELLOW, RED, BLOCKED)
    using regex pattern matching.
    """

    def __init__(self, custom_rules: Dict[RiskTier, List[str]] = None):
        self.rules: List[RiskPattern] = []
        self._initialize_defaults()
        if custom_rules:
            self._add_custom_rules(custom_rules)

    def _initialize_defaults(self):
        # BLOCKED: Fork bombs, system destruction, known malicious patterns
        self._add_rule(r":\(\)\{\s*:\|\s*:\s*&\s*\}\s*;", RiskTier.BLOCKED, "Fork bomb")
        self._add_rule(r"mkfs", RiskTier.BLOCKED, "Filesystem formatting")
        self._add_rule(r"dd\s+if=", RiskTier.BLOCKED, "Low-level disk writing")
        self._add_rule(r"> /dev/sd[a-z]", RiskTier.BLOCKED, "Raw device writing")
        
        # RED: High impact, destructive, permission changes
        self._add_rule(r"rm\s+.*(-r|-f|--recursive|--force)", RiskTier.RED, "Recursive/forced deletion")
        self._add_rule(r"chmod", RiskTier.RED, "Permission modification")
        self._add_rule(r"chown", RiskTier.RED, "Ownership modification")
        self._add_rule(r"sudo", RiskTier.RED, "Privilege escalation")
        self._add_rule(r"git\s+push\s+.*(--force|-f)", RiskTier.RED, "Force push")
        self._add_rule(r"systemctl\s+(stop|disable|mask)", RiskTier.RED, "Service modification")

        # YELLOW: Network, external mutations, non-recursive deletion
        self._add_rule(r"rm\s+[^-]", RiskTier.YELLOW, "File deletion")
        self._add_rule(r"curl", RiskTier.YELLOW, "Network request (curl)")
        self._add_rule(r"wget", RiskTier.YELLOW, "Network request (wget)")
        self._add_rule(r"git\s+push", RiskTier.YELLOW, "Git push")
        self._add_rule(r"ssh", RiskTier.YELLOW, "SSH connection")
        self._add_rule(r"npm\s+(publish|i|install)", RiskTier.YELLOW, "Package installation/publishing")
        self._add_rule(r"pip\s+install", RiskTier.YELLOW, "Package installation")

        # GREEN: specific safe read-only commands
        # Note: Default for unknown commands should be YELLOW/RED, not GREEN.
        # We explicit define GREEN for known safe ops.
        self._add_rule(r"^ls(\s|$)", RiskTier.GREEN, "List directory")
        self._add_rule(r"^pwd(\s|$)", RiskTier.GREEN, "Print working directory")
        self._add_rule(r"^echo(\s|$)", RiskTier.GREEN, "Echo")
        self._add_rule(r"^cat(\s|$)", RiskTier.GREEN, "Read file")
        self._add_rule(r"^git\s+status", RiskTier.GREEN, "Git status")
        self._add_rule(r"^git\s+log", RiskTier.GREEN, "Git log")
        self._add_rule(r"^grep", RiskTier.GREEN, "Grep search")
        self._add_rule(r"^find", RiskTier.GREEN, "Find files")

    def _add_rule(self, pattern_str: str, tier: RiskTier, description: str):
        try:
            pattern = re.compile(pattern_str, re.IGNORECASE)
            self.rules.append(RiskPattern(pattern=pattern, tier=tier, description=description))
        except re.error as e:
            logger.error("invalid_risk_pattern", pattern=pattern_str, error=str(e))

    def _add_custom_rules(self, custom_rules: Dict[RiskTier, List[str]]):
        for tier, patterns in custom_rules.items():
            for p in patterns:
                self._add_rule(p, tier, "Custom rule")

    def classify(self, command: str, config=None) -> RiskTier:
        """
        Determines the risk tier for a command.
        
        Priority: 
        1. Blocklist (Exact Prefix) -> BLOCKED
        2. Allowlist (Exact Prefix) -> GREEN
        3. Regex Patterns -> Matched Tier
        4. Default -> YELLOW
        """
        # 1. Check Allowlist/Blocklist if config provided
        if config:
            # Blocklist (highest priority)
            for blocked in config.blocklist:
                if command.startswith(blocked):
                    return RiskTier.BLOCKED
            
            # Allowlist
            for allowed in config.allowlist:
                if command.startswith(allowed):
                    return RiskTier.GREEN
        
        # 2. Regex Pattern Matching
        highest_risk = RiskTier.GREEN
        
        # We need a hierarchy to compare tiers
        tier_severity = {
            RiskTier.BLOCKED: 4,
            RiskTier.RED: 3,
            RiskTier.YELLOW: 2,
            RiskTier.GREEN: 1
        }

        matched_rule = None

        for rule in self.rules:
            if rule.pattern.search(command):
                if tier_severity[rule.tier] > tier_severity[highest_risk]:
                    highest_risk = rule.tier
                    matched_rule = rule

        # If no regex matched, what is the default?
        # A conservative default is YELLOW (Gatekeeper required).
        # GREEN is only allowed if explicit match.
        if highest_risk == RiskTier.GREEN and matched_rule is None:
            # No GREEN match found, and no higher match found -> Unknown command
            return RiskTier.YELLOW
        
        return highest_risk
