#!/usr/bin/env python3
"""
Bridge Backend Import Verification Engine v1.9.4a+
Validates critical imports before application startup
Part of the Render Runtime Import Fix (v1.9.4a+)
"""
import importlib
import logging
import sys
import os

# Add repository root to path for imports (parent of bridge_backend)
repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, repo_root)

logging.basicConfig(level=logging.INFO)

def check_critical_imports():
    """
    Verify all critical modules can be imported.
    Returns a dict of module names to status strings.
    """
    critical = [
        "bridge_backend.models",
        "bridge_backend.runtime.auto_repair",
        "bridge_backend.main",
    ]
    
    results = {}
    all_ok = True
    
    for module in critical:
        try:
            importlib.import_module(module)
            results[module] = "✅ OK"
            logging.info(f"[IMPORT CHECK] {module}: ✅ OK")
        except Exception as e:
            results[module] = f"❌ {e}"
            logging.error(f"[IMPORT CHECK] {module}: ❌ {e}")
            all_ok = False
    
    if all_ok:
        logging.info("[DIAG] ✅ All critical imports verified")
    else:
        logging.error("[DIAG] ❌ Some imports failed - check logs above")
    
    return results

if __name__ == "__main__":
    """Run import verification when called directly"""
    print("=" * 60)
    print("SR-AIbridge v1.9.4a+ — Import Verification")
    print("=" * 60)
    
    results = check_critical_imports()
    
    # Exit with error code if any imports failed
    if any("❌" in status for status in results.values()):
        print("\n⚠️  Import verification failed - see errors above")
        sys.exit(1)
    else:
        print("\n✅ Import verification complete - all modules OK")
        sys.exit(0)
