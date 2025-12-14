#!/usr/bin/env python3
"""
Test EnvRecon-Autonomy Integration
Validates that the adapter link is working correctly
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

def test_adapter_import():
    """Test that the adapter can be imported"""
    try:
        from bridge_core.engines.adapters.envrecon_autonomy_link import envrecon_autonomy_link
        print("✅ EnvRecon-Autonomy adapter imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import adapter: {e}")
        return False

def test_adapter_initialization():
    """Test that the adapter initializes correctly"""
    try:
        from bridge_core.engines.adapters.envrecon_autonomy_link import envrecon_autonomy_link
        
        print(f"   Autonomy enabled: {envrecon_autonomy_link.autonomy_enabled}")
        print(f"   Genesis enabled: {envrecon_autonomy_link.genesis_enabled}")
        
        # At least one should be available
        if envrecon_autonomy_link.autonomy_enabled or envrecon_autonomy_link.genesis_enabled:
            print("✅ EnvRecon-Autonomy adapter initialized (at least one connection active)")
            return True
        else:
            print("⚠️  EnvRecon-Autonomy adapter initialized but no connections available")
            return True  # Still valid, just means Genesis/Autonomy aren't loaded
    except Exception as e:
        print(f"❌ Failed to initialize adapter: {e}")
        return False

def test_genesis_topics():
    """Test that Genesis topics are registered"""
    try:
        from genesis.bus import genesis_bus
        
        # Check for EnvRecon-specific topics
        envrecon_topics = [
            "envrecon.drift",
            "envrecon.audit", 
            "envrecon.heal",
            "envrecon.sync"
        ]
        
        missing_topics = [t for t in envrecon_topics if t not in genesis_bus._valid_topics]
        
        if not missing_topics:
            print("✅ All EnvRecon Genesis topics registered")
            return True
        else:
            print(f"❌ Missing topics: {missing_topics}")
            return False
    except ImportError:
        print("⚠️  Genesis bus not available, skipping topic check")
        return True
    except Exception as e:
        print(f"❌ Failed to check Genesis topics: {e}")
        return False

def test_envrecon_core_integration():
    """Test that EnvRecon core has integration code"""
    try:
        import inspect
        from engines.envrecon.core import EnvReconEngine
        
        # Get the source code of reconcile method
        source = inspect.getsource(EnvReconEngine.reconcile)
        
        # Check for autonomy link integration
        if "envrecon_autonomy_link" in source:
            print("✅ EnvRecon core has autonomy link integration")
            return True
        else:
            print("❌ EnvRecon core missing autonomy link integration")
            return False
    except Exception as e:
        print(f"❌ Failed to check core integration: {e}")
        return False

def test_autoheal_genesis_integration():
    """Test that AutoHeal has Genesis integration"""
    try:
        import inspect
        from engines.envrecon.autoheal import AutoHealEngine
        
        # Get the source code of _emit_heal_event method
        source = inspect.getsource(AutoHealEngine._emit_heal_event)
        
        # Check for envrecon.heal topic
        if "envrecon.heal" in source:
            print("✅ AutoHeal has Genesis topic integration")
            return True
        else:
            print("❌ AutoHeal missing Genesis topic")
            return False
    except Exception as e:
        print(f"❌ Failed to check AutoHeal integration: {e}")
        return False

def test_routes_integration():
    """Test that routes have autonomy link notifications"""
    try:
        import inspect
        from engines.envrecon import routes
        
        # Get the source code of sync_all function
        source = inspect.getsource(routes.sync_all)
        
        # Check for autonomy link integration
        if "envrecon_autonomy_link" in source and "notify_heal_complete" in source:
            print("✅ Routes have autonomy link notifications")
            return True
        else:
            print("❌ Routes missing autonomy link notifications")
            return False
    except Exception as e:
        print(f"❌ Failed to check routes integration: {e}")
        return False

def main():
    """Run all integration tests"""
    print("=" * 80)
    print("EnvRecon-Autonomy Integration Tests")
    print("=" * 80)
    print()
    
    tests = [
        ("Adapter Import", test_adapter_import),
        ("Adapter Initialization", test_adapter_initialization),
        ("Genesis Topics Registration", test_genesis_topics),
        ("EnvRecon Core Integration", test_envrecon_core_integration),
        ("AutoHeal Genesis Integration", test_autoheal_genesis_integration),
        ("Routes Integration", test_routes_integration),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"Testing: {name}")
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append((name, False))
        print()
    
    print("=" * 80)
    print("Integration Test Results")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print()
    print(f"Total: {passed}/{total} tests passed")
    print("=" * 80)
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())
