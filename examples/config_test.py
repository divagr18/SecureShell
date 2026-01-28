import asyncio
from secureshell import SecureShell
from secureshell.providers.openai import OpenAI

async def main():
    # Initialize shell (will load secueshell.yaml)
    # Use dummy provider since we testing config bypass
    shell = SecureShell(provider=OpenAI(api_key="sk-dummy"))
    shell.config.debug_mode = True
    
    print("🚀 Testing Whitelist/Blacklist Logic\n")
    
    # 1. Test Whitelist (Should bypass Gatekeeper)
    # 'rm' is usually Yellow/Red, so without whitelist it would trigger Gatekeeper (and fail with dummy key)
    print("--- Test 1: Whitelisted Command ---")
    res1 = await shell.execute("rm safe_delete.txt", "cleaning up")
    print(f"Command: rm safe_delete.txt")
    print(f"Success: {res1.success}")
    print(f"Meta: {res1.risk_tier}") # Should be GREEN if allowlisted
    print("\n")

    # 2. Test Blacklist
    print("--- Test 2: Blacklisted Command ---")
    res2 = await shell.execute("echo blocked_message", "just echoing")
    print(f"Command: echo blocked_message")
    print(f"Success: {res2.success}")
    print(f"Reason: {res2.denial_reason}")
    print("\n")
    
    # 3. Test Normal
    print("--- Test 3: Normal Command ---")
    res3 = await shell.execute("echo normal_message", "just echoing")
    print(f"Command: echo normal_message")
    print(f"Success: {res3.success}")
    
    await shell.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
