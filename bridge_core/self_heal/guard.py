#!/usr/bin/env python3
"""
Bridge Core Validation Guard
Validates core system components before deployment
"""
import sys
import argparse


def check_core_validation():
    """
    Validate core bridge components.
    Returns 0 on success, non-zero on failure.
    """
    print("🛡️  Running Core Validation Guard...")

    # Basic checks
    checks_passed = True

    # Check 1: Python version
    python_version = sys.version_info
    if python_version >= (3, 11):
        print(f"  ✅ Python version: {python_version.major}.{python_version.minor}")
    else:
        print(f"  ❌ Python version too old: {python_version.major}.{python_version.minor}")
        checks_passed = False

    # Check 2: Module structure
    try:
        import bridge_core  # noqa: F401
        print("  ✅ bridge_core module accessible")
    except ImportError:
        print("  ❌ bridge_core module not found")
        checks_passed = False

    if checks_passed:
        print("✅ Core validation complete - all checks passed")
        return 0
    else:
        print("❌ Core validation failed - see errors above")
        return 1


def main():
    parser = argparse.ArgumentParser(description="Bridge Core Validation Guard")
    parser.add_argument("--check", action="store_true", help="Run validation checks")
    args = parser.parse_args()

    if args.check:
        sys.exit(check_core_validation())
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
