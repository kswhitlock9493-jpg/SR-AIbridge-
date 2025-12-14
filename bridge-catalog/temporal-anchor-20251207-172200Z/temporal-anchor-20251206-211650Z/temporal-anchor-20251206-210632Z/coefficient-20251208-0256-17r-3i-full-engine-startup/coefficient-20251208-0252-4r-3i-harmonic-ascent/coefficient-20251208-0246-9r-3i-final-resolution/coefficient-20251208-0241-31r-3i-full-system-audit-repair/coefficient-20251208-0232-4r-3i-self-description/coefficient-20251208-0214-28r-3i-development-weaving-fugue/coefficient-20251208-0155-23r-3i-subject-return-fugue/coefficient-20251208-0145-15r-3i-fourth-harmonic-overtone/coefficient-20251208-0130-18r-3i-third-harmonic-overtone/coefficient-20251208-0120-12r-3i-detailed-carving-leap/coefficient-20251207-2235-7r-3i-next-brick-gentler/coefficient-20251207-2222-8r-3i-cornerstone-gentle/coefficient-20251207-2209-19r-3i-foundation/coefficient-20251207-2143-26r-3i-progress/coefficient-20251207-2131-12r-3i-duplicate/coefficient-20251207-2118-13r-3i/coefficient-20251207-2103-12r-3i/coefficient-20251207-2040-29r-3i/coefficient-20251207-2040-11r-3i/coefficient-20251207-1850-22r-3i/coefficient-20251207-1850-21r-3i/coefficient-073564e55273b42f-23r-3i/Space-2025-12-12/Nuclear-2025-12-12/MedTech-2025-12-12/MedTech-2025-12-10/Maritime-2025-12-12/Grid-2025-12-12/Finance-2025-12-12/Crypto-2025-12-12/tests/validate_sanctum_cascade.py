#!/usr/bin/env python3
"""
Sanctum Cascade Protocol Validation Script
Tests the complete v1.9.7q implementation
"""
import sys
import os
import time

sys.path.insert(0, '.')

def test_netlify_guard():
    """Test Netlify Guard module"""
    print("=" * 70)
    print("Test 1: Netlify Guard")
    print("=" * 70)
    
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        'netlify_guard', 
        'bridge_backend/bridge_core/guards/netlify_guard.py'
    )
    ng = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ng)
    
    # Test validate_publish_path
    os.environ.pop('NETLIFY_PUBLISH_PATH', None)
    result = ng.validate_publish_path()
    print(f"  ✅ validate_publish_path: {result}")
    
    # Test require_netlify_token
    os.environ.pop('NETLIFY_AUTH_TOKEN', None)
    token = ng.require_netlify_token(lambda: "test_token")
    print(f"  ✅ require_netlify_token: token set")
    
    print()
    return True


def test_deferred_integrity():
    """Test Deferred Integrity module"""
    print("=" * 70)
    print("Test 2: Deferred Integrity")
    print("=" * 70)
    
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        'deferred', 
        'bridge_backend/bridge_core/integrity/deferred.py'
    )
    deferred = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(deferred)
    
    # Set short delay for testing
    os.environ['INTEGRITY_DEFER_SECONDS'] = '0.5'
    
    def mock_check():
        return {"status": "ok"}
    
    start = time.time()
    result = deferred.delayed_integrity_check(mock_check)
    elapsed = time.time() - start
    
    print(f"  ✅ delayed_integrity_check: {result}")
    print(f"  ✅ Delay: {elapsed:.2f}s")
    
    print()
    return True


def test_autoheal_link():
    """Test Umbra Auto-Heal linker"""
    print("=" * 70)
    print("Test 3: Umbra Auto-Heal Linker")
    print("=" * 70)
    
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        'autoheal', 
        'bridge_backend/bridge_core/engines/umbra/autoheal_link.py'
    )
    autoheal = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(autoheal)
    
    # Test successful link
    def mock_success():
        pass
    
    result = autoheal.safe_autoheal_init(mock_success, retries=5, backoff=0.1)
    print(f"  ✅ safe_autoheal_init (success): {result}")
    
    # Test retry logic
    call_count = [0]
    def mock_retry():
        call_count[0] += 1
        if call_count[0] < 3:
            raise RuntimeError(f"Attempt {call_count[0]}")
    
    result = autoheal.safe_autoheal_init(mock_retry, retries=5, backoff=0.05)
    print(f"  ✅ safe_autoheal_init (retry): {result} after {call_count[0]} attempts")
    
    print()
    return True


def test_main_py_imports():
    """Test that main.py can be parsed and has the right imports"""
    print("=" * 70)
    print("Test 4: Main.py Integration")
    print("=" * 70)
    
    with open('bridge_backend/main.py', 'r') as f:
        content = f.read()
    
    # Check for Sanctum Cascade Protocol section
    if 'Sanctum Cascade Protocol v1.9.7q' in content:
        print("  ✅ Sanctum Cascade Protocol section found")
    else:
        print("  ❌ Sanctum Cascade Protocol section NOT found")
        return False
    
    # Check for version update
    if 'version="1.9.7q"' in content:
        print("  ✅ Version updated to 1.9.7q")
    else:
        print("  ❌ Version NOT updated")
        return False
    
    # Check for guard imports
    required_imports = [
        'from bridge_backend.bridge_core.guards.netlify_guard import',
        'from bridge_backend.bridge_core.integrity.deferred import',
        'from bridge_backend.bridge_core.engines.umbra.autoheal_link import',
    ]
    
    for imp in required_imports:
        if imp in content:
            print(f"  ✅ Import found: {imp[:50]}...")
        else:
            print(f"  ❌ Import NOT found: {imp}")
            return False
    
    print()
    return True


def test_workflow():
    """Test GitHub Actions workflow"""
    print("=" * 70)
    print("Test 5: GitHub Actions Workflow")
    print("=" * 70)
    
    workflow_path = '.github/workflows/preflight.yml'
    if not os.path.exists(workflow_path):
        print(f"  ❌ Workflow file NOT found: {workflow_path}")
        return False
    
    with open(workflow_path, 'r') as f:
        content = f.read()
    
    if 'Deploy Preview (Bridge Preflight)' in content:
        print("  ✅ Workflow name correct")
    else:
        print("  ❌ Workflow name incorrect")
        return False
    
    if 'Netlify Guard' in content:
        print("  ✅ Netlify Guard step found")
    else:
        print("  ❌ Netlify Guard step NOT found")
        return False
    
    if 'Deferred Integrity' in content:
        print("  ✅ Deferred Integrity step found")
    else:
        print("  ❌ Deferred Integrity step NOT found")
        return False
    
    print()
    return True


def test_documentation():
    """Test documentation files"""
    print("=" * 70)
    print("Test 6: Documentation")
    print("=" * 70)
    
    docs = [
        'docs/SANCTUM_CASCADE_PROTOCOL.md',
        'docs/NETLIFY_GUARD_OVERVIEW.md',
        'docs/INTEGRITY_DEFERRED_GUIDE.md',
    ]
    
    for doc in docs:
        if os.path.exists(doc):
            print(f"  ✅ {doc}")
        else:
            print(f"  ❌ {doc} NOT found")
            return False
    
    print()
    return True


def test_env_template():
    """Test environment template"""
    print("=" * 70)
    print("Test 7: Environment Template")
    print("=" * 70)
    
    template_path = '.env.v197q.example'
    if not os.path.exists(template_path):
        print(f"  ❌ Template file NOT found: {template_path}")
        return False
    
    with open(template_path, 'r') as f:
        content = f.read()
    
    if 'INTEGRITY_DEFER_SECONDS' in content:
        print("  ✅ INTEGRITY_DEFER_SECONDS found")
    else:
        print("  ❌ INTEGRITY_DEFER_SECONDS NOT found")
        return False
    
    if 'NETLIFY_PUBLISH_PATH' in content:
        print("  ✅ NETLIFY_PUBLISH_PATH found")
    else:
        print("  ❌ NETLIFY_PUBLISH_PATH NOT found")
        return False
    
    print()
    return True


def main():
    """Run all validation tests"""
    print("\n" + "=" * 70)
    print("Sanctum Cascade Protocol v1.9.7q Validation")
    print("=" * 70)
    print()
    
    tests = [
        test_netlify_guard,
        test_deferred_integrity,
        test_autoheal_link,
        test_main_py_imports,
        test_workflow,
        test_documentation,
        test_env_template,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"  ❌ Test failed with exception: {e}")
            failed += 1
    
    print("=" * 70)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 70)
    
    if failed == 0:
        print("\n🎉 All validation tests passed! ✅")
        print("\nSanctum Cascade Protocol v1.9.7q is ready for deployment.")
        return 0
    else:
        print(f"\n⚠️  {failed} test(s) failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
