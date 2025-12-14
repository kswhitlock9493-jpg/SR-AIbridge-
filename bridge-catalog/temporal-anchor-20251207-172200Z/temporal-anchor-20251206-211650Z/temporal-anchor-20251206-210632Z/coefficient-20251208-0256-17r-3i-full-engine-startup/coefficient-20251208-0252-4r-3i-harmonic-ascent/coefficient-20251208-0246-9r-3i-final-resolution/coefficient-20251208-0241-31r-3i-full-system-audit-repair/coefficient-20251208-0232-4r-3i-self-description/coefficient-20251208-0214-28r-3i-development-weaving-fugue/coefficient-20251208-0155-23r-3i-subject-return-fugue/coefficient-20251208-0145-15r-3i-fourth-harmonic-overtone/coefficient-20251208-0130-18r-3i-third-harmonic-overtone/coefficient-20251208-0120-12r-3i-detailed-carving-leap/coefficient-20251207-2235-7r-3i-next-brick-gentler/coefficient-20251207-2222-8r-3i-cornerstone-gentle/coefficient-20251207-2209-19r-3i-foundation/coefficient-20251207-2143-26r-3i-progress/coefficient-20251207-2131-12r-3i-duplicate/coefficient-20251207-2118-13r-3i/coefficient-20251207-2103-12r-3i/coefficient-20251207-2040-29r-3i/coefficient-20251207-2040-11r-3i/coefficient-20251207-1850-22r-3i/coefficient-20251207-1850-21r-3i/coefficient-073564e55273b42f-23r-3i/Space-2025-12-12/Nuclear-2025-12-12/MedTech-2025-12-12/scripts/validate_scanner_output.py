#!/usr/bin/env python3
"""
Verifies that all Netlify scanner outputs are non-blocking and valid.
This script checks for secret scanner false positives and ensures compliance.
"""

import re
import sys
import json
import subprocess
from pathlib import Path


def check_netlify_build_log():
    """Check if netlify build log exists and contains secret scanner warnings."""
    log_path = Path("netlify_build.log")
    
    if not log_path.exists():
        print("ℹ️  No netlify_build.log found. Skipping scanner validation.")
        print("   (This is expected in local/CI environments)")
        return True
    
    log_content = log_path.read_text()
    
    # Check for secret scanner warnings
    if re.search(r"Secrets scanning found \d+ instance", log_content, re.IGNORECASE):
        print("❌ Secret scanner still detecting false positives.")
        print("\nLog excerpt:")
        # Show relevant lines
        for line in log_content.split('\n'):
            if 'secret' in line.lower() or 'scan' in line.lower():
                print(f"   {line}")
        return False
    
    print("✅ No secrets detected by Netlify scanner.")
    return True


def check_scanner_config():
    """Verify netlify.toml has proper scanner configuration."""
    print("\n🔍 Validating netlify.toml scanner configuration...")
    
    try:
        import toml
    except ImportError:
        print("⚠️  toml package not installed. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "toml", "-q"], check=True)
        import toml
    
    config_path = Path("netlify.toml")
    if not config_path.exists():
        print("❌ netlify.toml not found!")
        return False
    
    config = toml.load(config_path)
    
    # Check scanner is enabled (not disabled)
    build_env = config.get('build', {}).get('environment', {})
    scanner_enabled = build_env.get('SECRETS_SCAN_ENABLED', 'false')
    
    if scanner_enabled.lower() == 'false':
        print("⚠️  Warning: SECRETS_SCAN_ENABLED is set to 'false'")
        print("   v1.6.4 should use legitimate compliance, not suppression.")
        return False
    
    # Check for proper omit configuration
    secrets_scan_config = config.get('build', {}).get('processing', {}).get('secrets_scan', {})
    omit_paths = secrets_scan_config.get('omit', [])
    
    if not omit_paths:
        print("⚠️  No omit paths configured in [build.processing.secrets_scan]")
    else:
        print(f"✅ Scanner omit paths configured: {len(omit_paths)} paths")
        for path in omit_paths:
            print(f"   - {path}")
    
    # Check functions directory exists
    functions_dir = config.get('functions', {}).get('directory')
    if functions_dir:
        func_path = Path(functions_dir)
        if func_path.exists():
            print(f"✅ Functions directory exists: {functions_dir}")
        else:
            print(f"⚠️  Functions directory configured but not found: {functions_dir}")
            return False
    
    print("✅ Scanner configuration validated.")
    return True


def main():
    """Run all validation tests."""
    print("=" * 60)
    print("SR-AIbridge Netlify Scanner Compliance Validation")
    print("Version: 1.6.4")
    print("=" * 60)
    print()
    
    results = []
    
    # Run validation checks
    results.append(("Scanner Configuration", check_scanner_config()))
    results.append(("Build Log Validation", check_netlify_build_log()))
    
    # Summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")
        if not passed:
            all_passed = False
    
    print()
    if all_passed:
        print("🎉 All scanner validation tests passed!")
        return 0
    else:
        print("⚠️  Some validation tests failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
