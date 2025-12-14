#!/usr/bin/env python3
"""
v1.9.7c Genesis Linkage - Deployment Readiness Check
Validates all components are properly integrated and ready for deployment
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def check_imports():
    """Verify all new modules can be imported"""
    print("1. Checking module imports...")
    try:
        from bridge_backend.bridge_core.engines.blueprint.registry import BlueprintRegistry
        from bridge_backend.bridge_core.engines.blueprint.adapters import tde_link
        from bridge_backend.bridge_core.engines.blueprint.adapters import cascade_link
        from bridge_backend.bridge_core.engines.blueprint.adapters import truth_link
        from bridge_backend.bridge_core.engines.blueprint.adapters import autonomy_link
        from bridge_backend.bridge_core.engines.routes_linked import router
        print("   ✅ All modules import successfully")
        return True
    except Exception as e:
        print(f"   ❌ Import error: {e}")
        return False


def check_registry():
    """Verify Blueprint Registry functionality"""
    print("\n2. Checking Blueprint Registry...")
    try:
        from bridge_backend.bridge_core.engines.blueprint.registry import BlueprintRegistry
        
        # Load manifest
        manifest = BlueprintRegistry.load_all()
        if len(manifest) < 5:
            print(f"   ❌ Expected at least 5 engines, got {len(manifest)}")
            return False
        
        # Validate integrity
        validation = BlueprintRegistry.validate_manifest_integrity()
        if not validation["valid"]:
            print(f"   ❌ Manifest validation failed: {validation['errors']}")
            return False
        
        # Check key engines exist
        required_engines = ["tde_x", "blueprint", "cascade", "truth", "autonomy"]
        for engine in required_engines:
            if engine not in manifest:
                print(f"   ❌ Missing required engine: {engine}")
                return False
        
        print(f"   ✅ Registry working ({len(manifest)} engines, validation passed)")
        return True
    except Exception as e:
        print(f"   ❌ Registry error: {e}")
        return False


def check_orchestrator_integration():
    """Verify TDE-X orchestrator integration"""
    print("\n3. Checking TDE-X orchestrator integration...")
    try:
        # Check orchestrator file was modified
        orch_file = Path(__file__).parent.parent / "bridge_backend" / "runtime" / "tde_x" / "orchestrator.py"
        content = orch_file.read_text()
        
        if "tde_link" not in content:
            print("   ❌ TDE-X orchestrator not updated with tde_link import")
            return False
        
        if "preload_manifest" not in content:
            print("   ❌ TDE-X orchestrator missing preload_manifest call")
            return False
        
        print("   ✅ TDE-X orchestrator properly integrated")
        return True
    except Exception as e:
        print(f"   ❌ Orchestrator check error: {e}")
        return False


def check_main_integration():
    """Verify main.py integration"""
    print("\n4. Checking main.py integration...")
    try:
        main_file = Path(__file__).parent.parent / "bridge_backend" / "main.py"
        content = main_file.read_text()
        
        if "1.9.7c" not in content:
            print("   ❌ Version not updated to 1.9.7c")
            return False
        
        if "LINK_ENGINES" not in content:
            print("   ❌ LINK_ENGINES configuration missing")
            return False
        
        if "routes_linked" not in content:
            print("   ❌ routes_linked not imported")
            return False
        
        print("   ✅ main.py properly integrated")
        return True
    except Exception as e:
        print(f"   ❌ main.py check error: {e}")
        return False


def check_routes():
    """Verify linked routes exist"""
    print("\n5. Checking linked routes...")
    try:
        from bridge_backend.bridge_core.engines.routes_linked import router
        
        routes = [route.path for route in router.routes]
        expected_routes = [
            "/engines/linked/status",
            "/engines/linked/manifest",
            "/engines/linked/initialize"
        ]
        
        for expected in expected_routes:
            if expected not in routes:
                print(f"   ❌ Missing route: {expected}")
                return False
        
        print(f"   ✅ All linked routes present ({len(routes)} total)")
        return True
    except Exception as e:
        print(f"   ❌ Routes error: {e}")
        return False


def check_tests():
    """Verify test files exist"""
    print("\n6. Checking test files...")
    try:
        test_file = Path(__file__).parent / "test_v197c_genesis_linkage.py"
        integration_file = Path(__file__).parent / "integration_test_genesis_linkage.py"
        
        if not test_file.exists():
            print("   ❌ Unit test file missing")
            return False
        
        if not integration_file.exists():
            print("   ❌ Integration test file missing")
            return False
        
        print("   ✅ All test files present")
        return True
    except Exception as e:
        print(f"   ❌ Test check error: {e}")
        return False


def check_documentation():
    """Verify documentation exists"""
    print("\n7. Checking documentation...")
    try:
        guide = Path(__file__).parent.parent / "GENESIS_LINKAGE_GUIDE.md"
        quick_ref = Path(__file__).parent.parent / "GENESIS_LINKAGE_QUICK_REF.md"
        
        if not guide.exists():
            print("   ❌ GENESIS_LINKAGE_GUIDE.md missing")
            return False
        
        if not quick_ref.exists():
            print("   ❌ GENESIS_LINKAGE_QUICK_REF.md missing")
            return False
        
        print("   ✅ All documentation present")
        return True
    except Exception as e:
        print(f"   ❌ Documentation check error: {e}")
        return False


def main():
    """Run all readiness checks"""
    print("=" * 60)
    print("v1.9.7c Genesis Linkage - Deployment Readiness Check")
    print("=" * 60)
    
    checks = [
        ("Module Imports", check_imports),
        ("Blueprint Registry", check_registry),
        ("TDE-X Integration", check_orchestrator_integration),
        ("Main.py Integration", check_main_integration),
        ("API Routes", check_routes),
        ("Test Files", check_tests),
        ("Documentation", check_documentation)
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"   ❌ Unexpected error in {name}: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    all_passed = all(result for _, result in results)
    
    print("=" * 60)
    if all_passed:
        print("✅ ALL CHECKS PASSED - READY FOR DEPLOYMENT")
        print("=" * 60)
        print("\nDeployment Configuration:")
        print("  Start Command: python -m bridge_backend.run")
        print("  Health Check: /health/live")
        print("  Environment Variables:")
        print("    - LINK_ENGINES=true (to enable linkage)")
        print("    - BLUEPRINTS_ENABLED=true (to enable blueprint routes)")
        print("    - AUTONOMY_GUARDRAILS=strict")
        print("    - BLUEPRINT_SYNC=true")
        return 0
    else:
        print("❌ SOME CHECKS FAILED - NOT READY FOR DEPLOYMENT")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
