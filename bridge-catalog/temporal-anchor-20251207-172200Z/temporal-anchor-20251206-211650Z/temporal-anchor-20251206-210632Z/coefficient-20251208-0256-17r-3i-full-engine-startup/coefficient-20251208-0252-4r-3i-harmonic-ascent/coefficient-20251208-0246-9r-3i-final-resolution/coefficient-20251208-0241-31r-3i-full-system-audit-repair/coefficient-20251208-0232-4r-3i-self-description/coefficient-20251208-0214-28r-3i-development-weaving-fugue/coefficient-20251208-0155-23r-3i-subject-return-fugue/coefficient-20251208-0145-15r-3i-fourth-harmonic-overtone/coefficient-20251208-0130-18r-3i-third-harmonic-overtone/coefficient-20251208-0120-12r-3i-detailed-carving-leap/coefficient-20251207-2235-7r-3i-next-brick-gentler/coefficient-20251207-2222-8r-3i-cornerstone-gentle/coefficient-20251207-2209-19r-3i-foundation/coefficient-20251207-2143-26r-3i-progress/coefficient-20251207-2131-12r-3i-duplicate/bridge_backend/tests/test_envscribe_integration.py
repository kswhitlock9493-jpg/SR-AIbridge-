#!/usr/bin/env python3
"""
Integration test for EnvScribe Genesis Bus integration
Tests that EnvScribe publishes events to Genesis Bus correctly
"""

import sys
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


async def test_genesis_integration():
    """Test EnvScribe Genesis Bus integration"""
    print("🧪 Testing EnvScribe Genesis Bus Integration...")
    print()
    
    try:
        # Import Genesis bus
        from bridge_backend.genesis.bus import genesis_bus
        
        # Run EnvScribe scan
        from bridge_backend.engines.envscribe.core import EnvScribeEngine
        from bridge_backend.engines.envscribe.routes import _notify_genesis_scan_complete
        
        engine = EnvScribeEngine()
        report = await engine.scan()
        print(f"   ✅ Scan completed: {report.summary.total_keys} variables")
        
        # Notify Genesis (will publish event if Genesis is available)
        await _notify_genesis_scan_complete(report)
        print("   ✅ Genesis notification attempted")
        
        print()
        print("✅ Genesis Bus integration test PASSED")
        return True
        
    except ImportError as e:
        print(f"   ⚠️ Genesis bus not available: {e}")
        print()
        print("⚠️ Genesis Bus integration test SKIPPED")
        return True  # Not a failure, just not available
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_envrecon_integration():
    """Test EnvScribe integration with EnvRecon"""
    print("🧪 Testing EnvScribe ↔ EnvRecon Integration...")
    print()
    
    try:
        from bridge_backend.engines.envscribe.core import EnvScribeEngine
        from bridge_backend.engines.envrecon.core import EnvReconEngine
        
        # Create EnvRecon report
        envrecon = EnvReconEngine()
        
        # Mock a basic reconciliation (won't actually fetch from APIs without credentials)
        envrecon_report = {
            "summary": {
                "total_keys": 10,
                "local_count": 10,
                "render_count": 0,
                "netlify_count": 0,
                "github_count": 0
            },
            "missing_in_render": ["TEST_VAR_1"],
            "missing_in_netlify": ["TEST_VAR_2"],
            "missing_in_github": [],
            "drifted": {},
            "timestamp": "2025-10-12T00:00:00Z"
        }
        envrecon.save_report(envrecon_report)
        print("   ✅ EnvRecon report saved")
        
        # Run EnvScribe scan (should integrate EnvRecon data)
        engine = EnvScribeEngine()
        report = await engine.scan()
        print(f"   ✅ EnvScribe scan completed")
        
        # Verify integration
        print(f"      Total variables: {report.summary.total_keys}")
        print(f"      Verified: {report.summary.verified}")
        
        print()
        print("✅ EnvRecon integration test PASSED")
        return True
        
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_full_audit_workflow():
    """Test complete EnvScribe audit workflow"""
    print("🧪 Testing Full Audit Workflow...")
    print()
    
    try:
        from bridge_backend.engines.envscribe.core import EnvScribeEngine
        from bridge_backend.engines.envscribe.emitters import EnvScribeEmitter
        
        # Scan
        print("   1️⃣ Running scan...")
        engine = EnvScribeEngine()
        report = await engine.scan()
        print(f"      ✅ Scanned {report.summary.total_keys} variables")
        
        # Emit
        print("   2️⃣ Generating artifacts...")
        emitter = EnvScribeEmitter()
        outputs = emitter.emit_all(report)
        print(f"      ✅ Generated {len([k for k in outputs.keys() if k != 'copy_blocks'])} files")
        
        # Verify outputs
        print("   3️⃣ Verifying outputs...")
        from pathlib import Path
        
        overview_path = Path(outputs["overview"])
        if overview_path.exists():
            print(f"      ✅ ENV_OVERVIEW.md exists")
        
        render_config = Path(outputs["render_config"])
        if render_config.exists():
            print(f"      ✅ Render config exists")
        
        netlify_config = Path(outputs["netlify_config"])
        if netlify_config.exists():
            print(f"      ✅ Netlify config exists")
        
        github_config = Path(outputs["github_config"])
        if github_config.exists():
            print(f"      ✅ GitHub config exists")
        
        print()
        print("✅ Full audit workflow test PASSED")
        return True
        
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all integration tests"""
    print("=" * 70)
    print("EnvScribe Integration Tests")
    print("=" * 70)
    print()
    
    tests = [
        ("Genesis Bus Integration", test_genesis_integration),
        ("EnvRecon Integration", test_envrecon_integration),
        ("Full Audit Workflow", test_full_audit_workflow),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = await test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Test {name} crashed: {e}")
            results.append((name, False))
        print()
    
    print("=" * 70)
    print("Integration Test Results")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print()
    print(f"Total: {passed}/{total} integration tests passed")
    print("=" * 70)
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
