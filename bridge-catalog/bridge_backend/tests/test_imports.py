#!/usr/bin/env python3
"""
Tests for v1.9.6b components: bootstrap, middleware, heartbeat
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

def test_bootstrap_import():
    """Test that bootstrap module can be imported"""
    try:
        from bridge_backend.db.bootstrap import auto_sync_schema
        print("✅ bootstrap module imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import bootstrap: {e}")
        return False

def test_middleware_import():
    """Test that middleware module can be imported"""
    try:
        from bridge_backend.middleware.headers import HeaderSyncMiddleware
        print("✅ middleware module imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import middleware: {e}")
        return False

def test_heartbeat_import():
    """Test that heartbeat module can be imported"""
    try:
        from bridge_backend.runtime.heartbeat import send_heartbeat, run
        print("✅ heartbeat module imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import heartbeat: {e}")
        return False

def test_bootstrap_module_exists():
    """Test that bootstrap.py file exists"""
    root = Path(__file__).resolve().parents[1]
    bootstrap_path = root / "db" / "bootstrap.py"
    
    if bootstrap_path.exists():
        print("✅ bootstrap.py exists")
        return True
    else:
        print("❌ bootstrap.py not found")
        return False

def test_middleware_module_exists():
    """Test that headers.py middleware file exists"""
    root = Path(__file__).resolve().parents[1]
    middleware_path = root / "middleware" / "headers.py"
    
    if middleware_path.exists():
        print("✅ headers.py middleware exists")
        return True
    else:
        print("❌ headers.py middleware not found")
        return False

def test_bootstrap_has_auto_sync():
    """Test that bootstrap module has auto_sync_schema function"""
    try:
        from bridge_backend.db import bootstrap
        assert hasattr(bootstrap, 'auto_sync_schema')
        print("✅ bootstrap.auto_sync_schema exists")
        return True
    except Exception as e:
        print(f"❌ bootstrap.auto_sync_schema check failed: {e}")
        return False

def test_middleware_has_class():
    """Test that middleware module has HeaderSyncMiddleware class"""
    try:
        from bridge_backend.middleware import headers
        assert hasattr(headers, 'HeaderSyncMiddleware')
        print("✅ HeaderSyncMiddleware class exists")
        return True
    except Exception as e:
        print(f"❌ HeaderSyncMiddleware check failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("v1.9.6b Components - Test Suite")
    print("=" * 60)
    print()
    
    tests = [
        ("Bootstrap Import", test_bootstrap_import),
        ("Middleware Import", test_middleware_import),
        ("Heartbeat Import", test_heartbeat_import),
        ("Bootstrap File Exists", test_bootstrap_module_exists),
        ("Middleware File Exists", test_middleware_module_exists),
        ("Bootstrap Function", test_bootstrap_has_auto_sync),
        ("Middleware Class", test_middleware_has_class),
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
    
    sys.exit(0 if passed == total else 1)
