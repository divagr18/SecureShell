"""
Performance Profiling for SecureShell
--------------------------------------
Measures timing of different components to identify optimization opportunities.
"""
import asyncio
import time
import os
import platform
from contextlib import contextmanager

@contextmanager
def timer(name):
    """Context manager to time code blocks"""
    start = time.perf_counter()
    yield
    end = time.perf_counter()
    print(f"⏱️  {name:40s}: {(end - start)*1000:>8.2f}ms")

async def profile_quickstart():
    print("=" * 60)
    print("SecureShell Performance Profile")
    print("=" * 60)
    print()
    
    # 1. Import time
    with timer("Import SecureShell"):
        from secureshell import SecureShell
        from secureshell.providers.openai import OpenAI, OpenAITools
    
    with timer("Import OpenAI client"):
        from openai import OpenAI as OpenAIClient
    
    # 2. Initialization time
    with timer("Create SecureShell instance"):
        shell = SecureShell(
            provider=OpenAI(
                api_key=os.getenv("OPENAI_API_KEY") or "test-key",
                model="gpt-4.1-mini"
            ),
            os_info=f"{platform.system()} {platform.release()}"
        )
    
    with timer("Create OpenAI client"):
        client = OpenAIClient(api_key=os.getenv("OPENAI_API_KEY") or "test-key")
    
    with timer("Get tool definition"):
        tools = [OpenAITools.get_tool_definition()]
    
    # 3. Command execution without LLM
    print("\n--- Direct Command Execution ---")
    
    with timer("Execute safe command (echo)"):
        result = await shell.execute(
            command="echo 'test'",
            reasoning="Testing performance"
        )
    
    print(f"   Result: {result.success}")
    
    # 4. Component breakdown
    print("\n--- Component Analysis ---")
    
    # Test risk classification
    with timer("Risk classification (10 commands)"):
        for _ in range(10):
            _ = shell.risk_classifier.classify("echo test")
    
    # Test sandbox validation
    with timer("Sandbox validation (10 commands)"):
        for _ in range(10):
            _ = shell.sandbox.validate_command("echo test")
    
    # Test gatekeeper (if API key available)
    if os.getenv("OPENAI_API_KEY") and shell.gatekeeper:
        print("\n--- Gatekeeper Performance ---")
        with timer("Gatekeeper evaluation (YELLOW)"):
            gk_result = await shell.gatekeeper.assess(
                command="dir",
                reasoning="List files",
                risk_tier=shell.risk_classifier.classify("dir"),
                context={"os": shell.os_info}
            )
        print(f"   Decision: {gk_result.decision}")
    
    # 5. Full execution cycle
    print("\n--- Full Execution Cycle ---")
    with timer("Full execute() with gatekeeper"):
        result = await shell.execute(
            command="dir" if platform.system() == "Windows" else "ls",
            reasoning="Performance test - list files"
        )
    
    print(f"   Success: {result.success}")
    print(f"   Output length: {len(result.stdout) if result.stdout else 0} chars")
    
    # 6. Audit logging
    print("\n--- Audit Logging ---")
    with timer("Audit log write (async)"):
        await shell.audit_logger.log_execution(
            "test command",
            "test reason",
            {"test": "context"},
            result
        )
    
    await shell.shutdown()
    
    # 7. Memory usage (approximate)
    print("\n--- Memory Footprint ---")
    import sys
    print(f"   SecureShell instance: ~{sys.getsizeof(shell)} bytes")
    
    print("\n" + "=" * 60)
    print("Profile Complete")
    print("=" * 60)

async def profile_imports():
    """Profile individual module imports"""
    print("\n--- Import Breakdown ---")
    
    modules = [
        "secureshell.models",
        "secureshell.config",
        "secureshell.risk_engine",
        "secureshell.sandbox",
        "secureshell.gatekeeper",
        "secureshell.audit",
        "secureshell.providers.base",
        "secureshell.providers.openai",
    ]
    
    for module in modules:
        with timer(f"Import {module}"):
            __import__(module)

if __name__ == "__main__":
    # Run import profiling first
    asyncio.run(profile_imports())
    
    print("\n")
    
    # Run main profiling
    asyncio.run(profile_quickstart())
