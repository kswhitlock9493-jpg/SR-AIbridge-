#!/usr/bin/env python3
"""
Test suite for Genesis Inspector Panel UI
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


def test_ui_router_import():
    """Test that UI router can be imported"""
    try:
        from engines.envrecon.ui import ui_router
        assert ui_router is not None
        assert ui_router.prefix == "/genesis/envrecon"
        print("✅ UI router imported successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to import UI router: {e}")
        return False


def test_ui_endpoint_exists():
    """Test that inspector panel endpoint is defined"""
    try:
        from engines.envrecon.ui import inspector_panel
        assert inspector_panel is not None
        print("✅ Inspector panel endpoint exists")
        return True
    except Exception as e:
        print(f"❌ Failed to find inspector panel endpoint: {e}")
        return False


def run_tests():
    """Run all tests"""
    print("=" * 60)
    print("Inspector Panel UI - Test Suite")
    print("=" * 60)
    print()
    
    tests = [
        ("UI Router Import", test_ui_router_import),
        ("Inspector Panel Endpoint", test_ui_endpoint_exists),
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
    sys.exit(run_tests())
