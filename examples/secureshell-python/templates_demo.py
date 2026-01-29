"""
Security Templates Demo
-----------------------
Demonstrates all 4 pre-built security templates.

Usage:
    export OPENAI_API_KEY=sk-...
    python examples/templates_demo.py
"""
import asyncio
import os

# Load .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from secureshell import SecureShell
from secureshell.providers.openai import OpenAI


async def test_template(template_name: str):
    """Test a specific template with various commands."""
    print(f"\n{'='*60}")
    print(f"Testing Template: {template_name.upper()}")
    print(f"{'='*60}\n")
    
    shell = SecureShell(
        template=template_name,
        provider=None  # No gatekeeper for demo
    )
    
    print(f"Allowlist: {shell.config.allowlist}")
    print(f"Blocklist: {shell.config.blocklist}\n")
    
    # Test commands
    commands = [
        ("echo 'Hello from SecureShell!'", "greeting"),
        ("ls -la", "list files"),
        ("npm install", "install package"),
        ("rm test.txt", "delete file"),
        ("git status", "check git status")
    ]
    
    for cmd, reason in commands:
        result = await shell.execute(cmd, reason)
        status = "✅ ALLOWED" if result.success else "❌ BLOCKED"
        print(f"{status:12} | {cmd:30} | {result.denial_reason or 'Executed'}")
    
    await shell.shutdown()


async def main():
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Note: OPENAI_API_KEY not set - using no gatekeeper mode for demo")
        print("   Commands will be ALLOWED (allowlist) or BLOCKED (blocklist) only\n")
    
    print("🚀 SecureShell Security Templates Demo\n")
    print("This demo shows how different templates handle the same commands.\n")
    
    # Test all templates
    templates = ["paranoid", "development", "production", "ci_cd"]
    
    for template in templates:
        await test_template(template)
    
    # Summary
    print(f"\n{'='*60}")
    print("Summary")
    print(f"{'='*60}")
    print("""
    🔒 paranoid:     Most restrictive - max security
    🛠️  development:  Most permissive - developer friendly
    🏭 production:   Balanced - production safe
    🚀 ci_cd:        Build tool focused - CI/CD optimized
    
    Choose the template that matches your use case!
    See examples/SECURITY_TEMPLATES.md for full documentation.
    """)


if __name__ == "__main__":
    asyncio.run(main())
