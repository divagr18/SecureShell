"""
Challenge Mode Demo
-------------------
Demonstrates the CHALLENGE gatekeeper decision type.

The gatekeeper should return CHALLENGE when:
- Reasoning is vague or unclear
- Intent is ambiguous
- More information is needed to make a decision

Usage:
    export OPENAI_API_KEY=sk-...
    python examples/challenge_demo.py
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


async def main():
    if not os.getenv("OPENAI_API_KEY"):
        return print("❌ Set OPENAI_API_KEY")
    
    print("🚀 Challenge Mode Demo\n")
    
    shell = SecureShell(
        provider=OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            model="gpt-4.1-mini"
        )
    )
    shell.config.debug_mode = True
    
    # Test 1: Clear reasoning (should ALLOW)
    print("--- Test 1: Clear Reasoning (Should ALLOW) ---")
    res1 = await shell.execute(
        "dir",
        "List directory contents to understand project structure for development"
    )
    print(f"Success: {res1.success}")
    print(f"Decision: {res1.gatekeeper_response.decision if res1.gatekeeper_response else 'N/A'}\n")
    
    # Test 2: Vague reasoning (should CHALLENGE)
    print("--- Test 2: Vague Reasoning (May CHALLENGE) ---")
    res2 = await shell.execute(
        "rm temp.txt",
        "just testing"
    )
    print(f"Success: {res2.success}")
    print(f"Decision: {res2.gatekeeper_response.decision if res2.gatekeeper_response else 'N/A'}")
    print(f"Reason: {res2.denial_reason}\n")
    
    # Test 3: Ambiguous intent (should CHALLENGE)
    print("--- Test 3: Ambiguous Intent (May CHALLENGE) ---")
    res3 = await shell.execute(
        "git reset --hard",
        "need to fix something"
    )
    print(f"Success: {res3.success}")
    print(f"Decision: {res3.gatekeeper_response.decision if res3.gatekeeper_response else 'N/A'}")
    print(f"Reason: {res3.denial_reason}\n")
    
    await shell.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
