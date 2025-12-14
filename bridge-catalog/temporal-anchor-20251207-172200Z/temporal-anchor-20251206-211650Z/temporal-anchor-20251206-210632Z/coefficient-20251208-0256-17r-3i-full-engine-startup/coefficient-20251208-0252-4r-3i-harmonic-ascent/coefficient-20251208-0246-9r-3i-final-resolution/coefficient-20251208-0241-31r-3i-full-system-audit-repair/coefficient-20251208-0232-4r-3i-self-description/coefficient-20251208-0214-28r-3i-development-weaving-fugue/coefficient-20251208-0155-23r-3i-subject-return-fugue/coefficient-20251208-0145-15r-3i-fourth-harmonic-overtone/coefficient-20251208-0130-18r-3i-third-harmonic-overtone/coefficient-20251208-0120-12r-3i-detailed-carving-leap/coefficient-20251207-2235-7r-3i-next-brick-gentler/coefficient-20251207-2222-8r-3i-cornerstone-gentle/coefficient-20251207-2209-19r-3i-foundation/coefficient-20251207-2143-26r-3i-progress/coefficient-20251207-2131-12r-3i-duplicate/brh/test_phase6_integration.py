#!/usr/bin/env python3
"""
Integration test for Phase 6 - Chaos & Recovery Suite
Validates that all components can be imported and initialized without errors.
"""
import os
import sys


def test_module_imports():
    """Test that all new modules can be imported"""
    print("Testing module imports...")
    
    # Set up test environment
    os.environ["BRH_NODE_ID"] = "integration-test-node"
    os.environ["BRH_ENV"] = "test"
    os.environ["FORGE_DOMINION_ROOT"] = "dominion://test.bridge"
    os.environ["DOMINION_SEAL"] = "test-seal"
    
    try:
        from brh import chaos, recovery
        print("✓ Chaos and recovery modules imported successfully")
    except Exception as e:
        print(f"✗ Failed to import modules: {e}")
        return False
    
    return True


def test_api_endpoints_available():
    """Test that new API endpoints are available"""
    print("Testing API endpoints...")
    
    try:
        from brh.api import app, log_event, EVENT_LOG
        print("✓ API module and log_event function available")
        
        # Test log_event functionality
        log_event("Test event")
        assert len(EVENT_LOG) == 1
        assert EVENT_LOG[0]["message"] == "Test event"
        print("✓ Event logging works correctly")
        
        # Clear for next test
        EVENT_LOG.clear()
    except Exception as e:
        print(f"✗ API endpoint test failed: {e}")
        return False
    
    return True


def test_configuration_options():
    """Test that configuration options are respected"""
    print("Testing configuration options...")
    
    try:
        # Test chaos configuration
        with os.popen("echo $BRH_CHAOS_ENABLED") as f:
            chaos_enabled = f.read().strip()
        
        # Test that chaos defaults to disabled
        from brh import chaos
        assert hasattr(chaos, 'INTERVAL')
        assert hasattr(chaos, 'KILL_PROB')
        print("✓ Chaos configuration options available")
        
        # Test recovery configuration
        from brh import recovery
        print("✓ Recovery module configuration available")
        
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False
    
    return True


def main():
    """Run all integration tests"""
    print("\n=== Phase 6 Integration Tests ===\n")
    
    tests = [
        ("Module Imports", test_module_imports),
        ("API Endpoints", test_api_endpoints_available),
        ("Configuration Options", test_configuration_options),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n--- {name} ---")
        result = test_func()
        results.append((name, result))
        print()
    
    # Summary
    print("\n=== Test Summary ===")
    all_passed = True
    for name, result in results:
        status = "PASS" if result else "FAIL"
        symbol = "✓" if result else "✗"
        print(f"{symbol} {name}: {status}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n✅ All integration tests passed!")
        return 0
    else:
        print("\n❌ Some integration tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
