#!/usr/bin/env python3
"""
Deployment Verification Script for v1.9.6f
Run this after deployment to verify all v1.9.6f features are working correctly
"""
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

def test_port_resolution():
    """Test adaptive port resolution"""
    from bridge_backend.runtime.ports import resolve_port
    
    # Test with PORT set
    os.environ['PORT'] = '10000'
    port = resolve_port()
    assert port == 10000, f"Expected 10000, got {port}"
    
    # Test fallback
    del os.environ['PORT']
    port = resolve_port()
    assert port == 8000, f"Expected 8000 fallback, got {port}"
    
    return True

def test_watchdog():
    """Test startup watchdog"""
    from bridge_backend.runtime.startup_watchdog import StartupWatchdog
    
    wd = StartupWatchdog()
    wd.mark_port_resolved(10000)
    wd.mark_bind_confirmed()
    wd.mark_heartbeat_initialized()
    
    metrics = wd.get_metrics()
    assert 'bind_time' in metrics, "Missing bind_time metric"
    assert metrics['bind_time'] is not None, "bind_time not tracked"
    
    return True

def test_adaptive_bind():
    """Test adaptive bind check"""
    from bridge_backend.runtime.ports import adaptive_bind_check
    
    final_port, status = adaptive_bind_check('0.0.0.0', 8000)
    assert final_port in [8000, 10000], f"Unexpected port: {final_port}"
    assert status in ['ok', 'fallback_ok', 'both_occupied'], f"Unexpected status: {status}"
    
    return True

def test_version():
    """Test version is correct"""
    from bridge_backend.main import app
    assert app.version == "1.9.6f", f"Expected version 1.9.6f, got {app.version}"
    return True

def main():
    print("="*70)
    print("v1.9.6f Deployment Verification")
    print("="*70)
    
    tests = [
        ("Port Resolution", test_port_resolution),
        ("Startup Watchdog", test_watchdog),
        ("Adaptive Bind Check", test_adaptive_bind),
        ("Version Check", test_version),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            test_func()
            print(f"✓ {name}")
            passed += 1
        except Exception as e:
            print(f"✗ {name}: {e}")
            failed += 1
    
    print("="*70)
    print(f"Results: {passed}/{len(tests)} tests passed")
    print("="*70)
    
    if failed == 0:
        print("✅ All v1.9.6f features verified!")
        return 0
    else:
        print(f"⚠️ {failed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
