"""
YAML Configuration Demo
-----------------------
Demonstrates the allowlist/blocklist feature with command type matching.

The allowlist/blocklist now matches command TYPES (first word) instead of exact prefixes:
- If "echo" is in the allowlist, ALL echo commands are allowed (echo hello, echo *, etc.)
- If "rm" is in the blocklist, ALL rm commands are blocked (rm file.txt, rm -rf /, etc.)

Usage:
    python cookbook/config_test.py
"""
import asyncio
from secureshell import SecureShell

async def main():
    # Initialize shell (will load secureshell.yaml)
    # Use None provider so gatekeeper is disabled (testing config bypass)
    shell = SecureShell(provider=None)
    shell.config.debug_mode = True
    
    print("🚀 Testing Allowlist/Blocklist with Command Types\n")
    print(f"Loaded config - Allowlist: {shell.config.allowlist}")
    print(f"Loaded config - Blocklist: {shell.config.blocklist}\n")
    
    # Test 1: Allowlisted command type (echo is in allowlist)
    print("--- Test 1: Allowlisted Command Type ---")
    res1 = await shell.execute("echo 'This should work'", "testing allowlist")
    print(f"Success: {res1.success}")
    print(f"Risk Tier: {res1.risk_tier}")
    print(f"Output: {res1.stdout if res1.success else res1.denial_reason}\n")

    # Test 2: Blocklisted command type (rm is in blocklist)
    print("--- Test 2: Blocklisted Command Type ---")
    res2 = await shell.execute("rm some_file.txt", "trying to delete")
    print(f"Success: {res2.success}")
    print(f"Reason: {res2.denial_reason}\n")
    
    # Test 3: Normal command (ls is allowlisted)
    print("--- Test 3: Another Allowlisted Command ---")
    res3 = await shell.execute("ls -la", "listing files")
    print(f"Success: {res3.success}")
    print(f"Output: {res3.stdout[:100] if res3.success else res3.denial_reason}")
    
    await shell.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
