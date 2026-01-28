"""
Centralized Configuration for SecureShell.
Uses pydantic-settings for robust environment variable loading.
"""
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
import yaml
from pathlib import Path

class SecureShellConfig(BaseSettings):
    """
    Global configuration for SecureShell.
    Loads from environment variables (prefix: SECURESHELL_) or .env file.
    """
    model_config = SettingsConfigDict(
        env_prefix="SECURESHELL_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Core Settings
    app_name: str = "SecureShell"
    environment: str = "production"
    debug_mode: bool = Field(default=False, description="Enable verbose stdout debugging of SecureShell decisions")
    
    # Provider Settings
    provider: str = Field(default="openai", description="Default LLM provider to use")
    openai_api_key: Optional[str] = Field(default=None, description="API Key for OpenAI")
    anthropic_api_key: Optional[str] = Field(default=None, description="API Key for Anthropic")
    
    # Execution Settings
    default_timeout_seconds: int = Field(default=300, description="Max execution time for commands")
    max_output_bytes: int = Field(default=1_000_000, description="Max stdout/stderr capture size (1MB)")
    
    # Audit Settings
    audit_log_path: str = "secureshell_audit.jsonl"
    audit_queue_size: int = 1000

    # Risk Settings
    verify_ssl: bool = True
    
    # Allowlist/Blocklist (Configured via YAML)
    allowlist: List[str] = Field(default_factory=list, description="List of exact command prefixes to always ALLOW")
    blocklist: List[str] = Field(default_factory=list, description="List of exact command prefixes to always BLOCK")

    @classmethod
    def load(cls) -> "SecureShellConfig":
        """Load config from env vars and optional YAML file."""
        # Load env vars first
        config = cls()
        
        # Check for YAML config
        yaml_path = Path("secureshell.yaml")
        if yaml_path.exists():
            try:
                with open(yaml_path, "r") as f:
                    data = yaml.safe_load(f) or {}
                    
                    # Update lists if present
                    if "allowlist" in data:
                        config.allowlist = data["allowlist"]
                    if "blocklist" in data:
                        config.blocklist = data["blocklist"]
                        
            except Exception as e:
                print(f"⚠️ Failed to load secureshell.yaml: {e}")
        
        return config
