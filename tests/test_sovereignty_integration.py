#!/usr/bin/env python3
"""
Quick smoke test for sovereignty integration
"""

import asyncio
import sys
import os
from pathlib import Path

# Add repository to path
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root))
sys.path.insert(0, str(repo_root / "bridge_backend"))

async def test_sovereignty_integration():
    """Test sovereignty guard integration"""
    print("🔍 Testing Bridge Sovereignty Integration...\n")
    
    # Test 1: Module import
    print("Test 1: Importing sovereignty module...")
    try:
        from bridge_backend.bridge_core.sovereignty.readiness_gate import (
            BridgeSovereigntyGuard,
            get_sovereignty_guard,
            ensure_sovereignty,
        )
        print("✅ Module imported successfully\n")
    except Exception as e:
        print(f"❌ Module import failed: {e}\n")
        return False
    
    # Test 2: Guard initialization
    print("Test 2: Initializing sovereignty guard...")
    try:
        guard = BridgeSovereigntyGuard()
        await guard.initialize()
        print(f"✅ Guard initialized in state: {guard.state.value}\n")
    except Exception as e:
        print(f"❌ Initialization failed: {e}\n")
        return False
    
    # Test 3: Get sovereignty report
    print("Test 3: Getting sovereignty report...")
    try:
        report = await guard.get_sovereignty_report()
        print(f"   Perfection: {report.perfection_score:.2%}")
        print(f"   Harmony: {report.harmony_score:.2%}")
        print(f"   Resonance: {report.resonance_score:.2%}")
        print(f"   Sovereignty: {report.sovereignty_score:.2%}")
        print(f"   Engines: {report.engines_operational}/{report.engines_total}")
        print(f"   Ready: {report.is_ready}")
        print(f"   Sovereign: {report.is_sovereign}")
        print("✅ Report generated successfully\n")
    except Exception as e:
        print(f"❌ Report generation failed: {e}\n")
        return False
    
    # Test 4: Health check
    print("Test 4: Running health check...")
    try:
        health = await guard.health_check()
        print(f"   Status: {health['status']}")
        print(f"   State: {health['state']}")
        print(f"   Ready: {health['is_ready']}")
        print("✅ Health check passed\n")
    except Exception as e:
        print(f"❌ Health check failed: {e}\n")
        return False
    
    # Test 5: Global instance
    print("Test 5: Testing global sovereignty guard...")
    try:
        global_guard = await get_sovereignty_guard()
        print(f"✅ Global guard obtained (state: {global_guard.state.value})\n")
    except Exception as e:
        print(f"❌ Global guard failed: {e}\n")
        return False
    
    # Test 6: Ensure sovereignty
    print("Test 6: Testing ensure_sovereignty helper...")
    try:
        result = await ensure_sovereignty()
        print(f"   Result: {result}")
        print("✅ Ensure sovereignty completed\n")
    except Exception as e:
        print(f"❌ Ensure sovereignty failed: {e}\n")
        return False
    
    print("=" * 60)
    print("🎉 All sovereignty integration tests passed!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = asyncio.run(test_sovereignty_integration())
    sys.exit(0 if success else 1)
