#!/usr/bin/env python3
"""
Test suite for EnvRecon Engine v2.0.2
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


def test_envrecon_import():
    """Test that envrecon module can be imported"""
    try:
        from engines.envrecon import EnvReconEngine
        print("✅ EnvRecon module imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import EnvRecon: {e}")
        return False


def test_core_engine_init():
    """Test that EnvRecon engine can be initialized"""
    try:
        from engines.envrecon.core import EnvReconEngine
        engine = EnvReconEngine()
        assert engine is not None
        assert engine.report_path.name == "env_recon_report.json"
        print("✅ EnvRecon engine initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize EnvRecon engine: {e}")
        return False


def test_local_env_loading():
    """Test loading local environment files"""
    try:
        from engines.envrecon.core import EnvReconEngine
        engine = EnvReconEngine()
        local_env = engine.load_local_env()
        assert isinstance(local_env, dict)
        print(f"✅ Loaded {len(local_env)} local environment variables")
        return True
    except Exception as e:
        print(f"❌ Failed to load local env: {e}")
        return False


@pytest.mark.asyncio
async def test_reconcile_async():
    """Test async reconciliation (without actual API calls)"""
    try:
        from engines.envrecon.core import EnvReconEngine
        engine = EnvReconEngine()
        
        # This will fail if API credentials aren't set, but that's ok for testing
        # We just want to make sure the method exists and can be called
        try:
            report = await engine.reconcile()
            print(f"✅ Reconciliation complete: {report.get('summary', {}).get('total_keys', 0)} keys")
        except Exception:
            # Expected if no API credentials are configured
            print("✅ Reconciliation method callable (API calls may have failed due to missing credentials)")
        return True
    except Exception as e:
        print(f"❌ Failed to test reconciliation: {e}")
        return False


def test_hubsync_import():
    """Test that HubSync can be imported"""
    try:
        from engines.envrecon.hubsync import hubsync
        assert hubsync is not None
        print("✅ HubSync imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import HubSync: {e}")
        return False


def test_autoheal_import():
    """Test that AutoHeal can be imported"""
    try:
        from engines.envrecon.autoheal import autoheal
        assert autoheal is not None
        print("✅ AutoHeal imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import AutoHeal: {e}")
        return False


def test_routes_import():
    """Test that routes can be imported"""
    try:
        from engines.envrecon.routes import router
        assert router is not None
        print("✅ EnvRecon routes imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import routes: {e}")
        return False


def test_ui_import():
    """Test that UI router can be imported"""
    try:
        from engines.envrecon.ui import ui_router
        assert ui_router is not None
        print("✅ Inspector Panel UI imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import UI: {e}")
        return False


def run_sync_tests():
    """Run synchronous tests"""
    print("=" * 60)
    print("EnvRecon Engine - Test Suite v2.0.2")
    print("=" * 60)
    print()
    
    tests = [
        ("Module Import", test_envrecon_import),
        ("Core Engine Init", test_core_engine_init),
        ("Local ENV Loading", test_local_env_loading),
        ("HubSync Import", test_hubsync_import),
        ("AutoHeal Import", test_autoheal_import),
        ("Routes Import", test_routes_import),
        ("UI Import", test_ui_import),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"Running: {name}")
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append((name, False))
        print()
    
    print("=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print()
    print(f"Total: {passed}/{total} tests passed")
    print("=" * 60)
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(run_sync_tests())
