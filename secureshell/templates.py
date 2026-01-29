"""
Security Templates for SecureShell.
Pre-configured security profiles for common use cases.
"""
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class SecurityTemplate:
    """Defines a security template with allowlist/blocklist configuration."""
    name: str
    description: str
    allowlist: List[str]
    blocklist: List[str]
    

# Define available templates
TEMPLATES: Dict[str, SecurityTemplate] = {
    "paranoid": SecurityTemplate(
        name="paranoid",
        description="Very restrictive, minimal allowlist - for maximum security",
        allowlist=["ls", "pwd", "echo", "cat"],
        blocklist=["rm", "dd", "chmod", "chown", "sudo", "curl", "wget"]
    ),
    
    "development": SecurityTemplate(
        name="development",
        description="Permissive for local development - trusts developer actions",
        allowlist=["ls", "pwd", "echo", "cat", "git", "npm", "pip", "python", "node"],
        blocklist=["dd", "mkfs", "sudo"]
    ),
    
    "production": SecurityTemplate(
        name="production",
        description="Balanced for production environments - strict but functional",
        allowlist=["ls", "pwd", "echo", "cat"],
        blocklist=["rm", "dd", "chmod", "chown", "sudo", "mkfs"]
    ),
    
    "ci_cd": SecurityTemplate(
        name="ci_cd",
        description="Optimized for CI/CD pipelines - allows common build tools",
        allowlist=["ls", "git", "npm", "pip", "docker", "node", "python"],
        blocklist=["dd", "mkfs", "sudo"]
    )
}


def get_template(template_name: str) -> SecurityTemplate:
    """
    Get a security template by name.
    
    Args:
        template_name: Name of the template ('paranoid', 'development', 'production', 'ci_cd')
        
    Returns:
        SecurityTemplate instance
        
    Raises:
        ValueError: If template name is not recognized
    """
    if template_name not in TEMPLATES:
        available = ", ".join(TEMPLATES.keys())
        raise ValueError(
            f"Unknown template '{template_name}'. "
            f"Available templates: {available}"
        )
    return TEMPLATES[template_name]


def list_templates() -> List[str]:
    """Return list of available template names."""
    return list(TEMPLATES.keys())
