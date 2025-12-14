#!/usr/bin/env python3
"""
Test suite for HubSync GitHub Secrets Integration
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


def test_hubsync_configuration():
    """Test HubSync configuration check"""
    try:
        from engines.envrecon.hubsync import HubSync
        sync = HubSync()
        # Should return False if not configured
        is_configured = sync.is_configured()
        print(f"✅ HubSync configuration check: {is_configured}")
        return True
    except Exception as e:
        print(f"❌ Failed to check configuration: {e}")
        return False


def test_hubsync_dry_run_mode():
    """Test HubSync dry-run mode detection"""
    try:
        import os
        from engines.envrecon.hubsync import HubSync
        
        # Test with dry-run enabled
        os.environ["HUBSYNC_DRYRUN"] = "true"
        sync = HubSync()
        assert sync.dry_run == True
        
        # Test with dry-run disabled
        os.environ["HUBSYNC_DRYRUN"] = "false"
        sync2 = HubSync()
        assert sync2.dry_run == False
        
        print("✅ HubSync dry-run mode works correctly")
        return True
    except Exception as e:
        print(f"❌ Failed dry-run test: {e}")
        return False


@pytest.mark.asyncio
async def test_hubsync_autofix_unconfigured():
    """Test HubSync autofix when not configured"""
    try:
        from engines.envrecon.hubsync import HubSync
        sync = HubSync()
        
        # Clear credentials to test unconfigured state
        sync.github_token = None
        sync.github_repo = None
        
        result = await sync.autofix_github_secrets([
            {"name": "TEST_SECRET", "value": "test_value"}
        ])
        
        assert result["success"] == False
        assert "not configured" in result.get("error", "").lower()
        print("✅ HubSync correctly handles unconfigured state")
        return True
    except Exception as e:
        print(f"❌ Failed autofix test: {e}")
        return False


def run_sync_tests():
    """Run synchronous tests"""
    print("=" * 60)
    print("HubSync - Test Suite")
    print("=" * 60)
    print()
    
    tests = [
        ("Configuration Check", test_hubsync_configuration),
        ("Dry-Run Mode", test_hubsync_dry_run_mode),
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
