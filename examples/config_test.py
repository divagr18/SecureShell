import asyncio
from secureshell import SecureShell

async def main():
    # Initialize shell (will load secureshell.yaml)
    # Use None provider so gatekeeper is disabled (testing config bypass)
    shell = SecureShell(provider=None)
    shell.config.debug_mode = True
    
    print("🚀 Testing Whitelist/Blacklist Logic\n")
    print(f"Loaded config - Allowlist: {shell.config.allowlist}")
    print(f"Loaded config - Blocklist: {shell.config.blocklist}\n")
    
    # 1. Test Whitelist (Should bypass everything - no gatekeeper needed)
    print("--- Test 1: Whitelisted Command ---")
    res1 = await shell.execute("rm safe_delete.txt", "cleaning up")
    print(f"Success: {res1.success}")
    print(f"Risk Tier: {res1.risk_tier}")
    print(f"Reason: {res1.denial_reason or 'Command executed (or failed naturally)'}\n")

    # 2. Test Blacklist (Should be blocked immediately)
    print("--- Test 2: Blacklisted Command ---")
    res2 = await shell.execute("echo blocked_message", "just echoing")
    print(f"Success: {res2.success}")
    print(f"Reason: {res2.denial_reason}\n")
    
    # 3. Test Normal (Will be blocked due to no gatekeeper)
    print("--- Test 3: Normal Command (No Gatekeeper) ---")
    res3 = await shell.execute("echo normal_message", "just echoing")
    print(f"Success: {res3.success}")
    print(f"Reason: {res3.denial_reason or 'N/A'}")
    
    await shell.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
