#!/usr/bin/env python3
"""
Verification script for Umbra Lattice v1.9.7g implementation
Checks that all components are in place
"""

import os
import sys
from pathlib import Path

def check_file(path, description):
    """Check if a file exists"""
    exists = Path(path).exists()
    status = "✓" if exists else "✗"
    print(f"{status} {description}: {path}")
    return exists

def check_module(module_name, description):
    """Check if a module can be imported"""
    try:
        __import__(module_name)
        print(f"✓ {description}: {module_name}")
        return True
    except ImportError as e:
        print(f"✗ {description}: {module_name} ({e})")
        return False

def main():
    print("=" * 60)
    print("Umbra Lattice v1.9.7g Implementation Verification")
    print("=" * 60)
    print()
    
    checks = []
    
    # Core files
    print("Core Implementation Files:")
    checks.append(check_file("bridge_backend/bridge_core/engines/umbra/models.py", "Models"))
    checks.append(check_file("bridge_backend/bridge_core/engines/umbra/storage.py", "Storage"))
    checks.append(check_file("bridge_backend/bridge_core/engines/umbra/lattice.py", "Lattice Core"))
    checks.append(check_file("bridge_backend/bridge_core/engines/umbra/routes.py", "Routes"))
    print()
    
    # Adapters
    print("Genesis Adapters:")
    checks.append(check_file("bridge_backend/bridge_core/engines/adapters/umbra_genesis_link.py", "Genesis Link"))
    checks.append(check_file("bridge_backend/bridge_core/engines/adapters/umbra_truth_link.py", "Truth Link"))
    checks.append(check_file("bridge_backend/bridge_core/engines/adapters/umbra_cascade_link.py", "Cascade Link"))
    print()
    
    # CLI
    print("CLI Commands:")
    checks.append(check_file("bridge_backend/cli/umbra.py", "Umbra CLI"))
    print()
    
    # Tests
    print("Test Files:")
    checks.append(check_file("tests/test_umbra_lattice_core.py", "Core Tests"))
    checks.append(check_file("tests/test_umbra_routes.py", "Routes Tests"))
    print()
    
    # Documentation
    print("Documentation:")
    checks.append(check_file("docs/UMBRA_LATTICE_OVERVIEW.md", "Overview"))
    checks.append(check_file("docs/UMBRA_LATTICE_QUICK_START.md", "Quick Start"))
    checks.append(check_file("docs/UMBRA_LATTICE_SCHEMA.md", "Schema"))
    print()
    
    # Check CLI functionality
    print("CLI Verification:")
    cli_check = os.system("python3 -m bridge_backend.cli.umbra --help > /dev/null 2>&1") == 0
    if cli_check:
        print("✓ CLI is functional")
    else:
        print("✗ CLI has import errors")
    checks.append(cli_check)
    print()
    
    # Summary
    print("=" * 60)
    passed = sum(checks)
    total = len(checks)
    print(f"Summary: {passed}/{total} checks passed")
    
    if passed == total:
        print("✅ All components verified successfully!")
        return 0
    else:
        print("⚠️  Some components missing or have errors")
        return 1

if __name__ == "__main__":
    sys.exit(main())
