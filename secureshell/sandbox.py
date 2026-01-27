"""
Filesystem Sandboxing for SecureShell
--------------------------------------
Provides path-based validation to prevent file operations outside allowed directories.

This is a best-effort static analysis of command arguments. For enterprise-grade 
isolation, consider containerization (Docker, Podman) or OS-level sandboxing.
"""
import os
from pathlib import Path
from typing import List, Optional
import structlog

from secureshell.models import CheckResult, RiskTier

logger = structlog.get_logger()


class SandboxValidator:
    """
    Validates that file operations stay within allowed directories.
    
    Uses heuristic parsing to extract paths from commands and checks them
    against allow/block lists. Prevents directory traversal and unauthorized
    file access.
    
    Example:
        >>> validator = SandboxValidator(
        ...     allowed_paths=["/home/user/project"],
        ...     blocked_paths=["/home/user/project/.git"]
        ... )
        >>> result = validator.validate_command("cat /home/user/project/file.txt")
        >>> assert result.passed
    """

    def __init__(
        self, 
        allowed_paths: List[str], 
        blocked_paths: Optional[List[str]] = None
    ):
        """
        Initialize the sandbox validator.
        
        Args:
            allowed_paths: List of directory paths where operations are allowed.
            blocked_paths: Optional list of paths to explicitly block (even if in allowed).
        """
        # Resolve to absolute paths for consistent comparison
        self.allowed_paths = [Path(p).resolve() for p in allowed_paths]
        self.blocked_paths = [Path(p).resolve() for p in (blocked_paths or [])]
        
        if not blocked_paths:
            self._add_default_blocks()

    def _add_default_blocks(self):
        """
        Add platform-specific sensitive paths to block list.
        Currently a no-op, but could add defaults like:
        - Windows: C:/Windows/System32
        - Unix: /etc, /usr/bin
        """
        pass

    def validate_command(self, command: str) -> CheckResult:
        """
        Parse command for file paths and validate against sandbox rules.
        
        This is a heuristic best-effort check. It:
        1. Tokenizes the command
        2. Identifies tokens that look like file paths
        3. Resolves them to absolute paths
        4. Checks against allow/block lists
        
        Args:
            command: Shell command string to validate.
            
        Returns:
            CheckResult indicating if validation passed.
            
        Note:
            This is NOT a full shell parser. Complex commands with pipes,
            redirects, or escaped characters may be imperfectly parsed.
            For production use, combine with OS-level sandboxing.
        """
        tokens = command.split()
        potential_paths = []
        
        for token in tokens:
            # Skip command flags (e.g., -la, --verbose, /a, /s)
            if self._is_flag(token):
                continue
                
            # Detect tokens that look like file paths
            if '/' in token or '\\' in token:
                potential_paths.append(token)
        
        # Validate each potential path
        for p_str in potential_paths:
            # Handle flags with values (e.g., --output=/path/to/file)
            clean_p = p_str.split('=')[-1]
            
            try:
                # Resolve to absolute path
                if os.path.isabs(clean_p):
                    abs_path = Path(clean_p).resolve()
                else:
                    # Relative paths resolve from CWD
                    abs_path = Path(os.getcwd()).joinpath(clean_p).resolve()
                
                # Check if path is allowed
                if not self._is_allowed(abs_path):
                    logger.warning(
                        "sandbox_violation", 
                        path=str(abs_path), 
                        allowed=str(self.allowed_paths)
                    )
                    return CheckResult(
                        passed=False, 
                        risk_tier=RiskTier.BLOCKED,
                        reason=f"Path access denied: {abs_path}"
                    )
                     
            except Exception as e:
                # Path parsing errors are logged but don't auto-block
                # (to avoid false positives on unusual arguments)
                logger.debug("path_parse_error", token=clean_p, error=str(e))
                continue

        return CheckResult(passed=True)

    def _is_flag(self, token: str) -> bool:
        """
        Determine if a token is a command flag rather than a file path.
        
        Recognizes common flag patterns:
        - Unix/Linux: -x, -xyz, --flag
        - Windows: /a, /s, /q (short flags only)
        
        Args:
            token: Command token to check.
            
        Returns:
            True if token is a flag, False if it's likely a path.
        """
        # Unix/Linux flags: -x, --xxx
        if token.startswith('-'):
            return True
        
        # Windows flags: /x, but NOT full paths like C:/path or /etc/path
        if token.startswith('/'):
            # Short flags only (e.g., /a, /s, /q)
            # Paths have multiple slashes or are longer
            if len(token) <= 3 and token.count('/') == 1:
                return True
            # Otherwise likely a Unix path like /etc or /home
            return False
        
        return False

    def _is_allowed(self, path: Path) -> bool:
        """
        Check if a path is allowed by sandbox rules.
        
        Rules:
        1. If path is in blocked_paths, deny
        2. If path is in allowed_paths, allow
        3. Otherwise, deny
        
        Args:
            path: Absolute path to check.
            
        Returns:
            True if access is allowed, False otherwise.
        """
        # 1. Check explicit blocks first
        for blocked in self.blocked_paths:
            if self._is_subpath(path, blocked):
                return False

        # 2. Check if inside any allowed path
        for allowed in self.allowed_paths:
            if self._is_subpath(path, allowed):
                return True
        
        # 3. Default deny
        return False

    def _is_subpath(self, child: Path, parent: Path) -> bool:
        """
        Check if child is a subpath of parent.
        
        Args:
            child: Potential child path.
            parent: Potential parent path.
            
        Returns:
            True if child is inside parent directory tree.
        """
        try:
            child.relative_to(parent)
            return True
        except ValueError:
            return False
