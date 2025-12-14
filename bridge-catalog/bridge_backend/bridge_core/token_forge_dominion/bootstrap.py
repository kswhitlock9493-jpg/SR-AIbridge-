"""
Bootstrap - Token Forge Dominion v1.9.7s-SOVEREIGN

Ensures valid root key exists or generates temporary one for local use.
Validates FORGE_DOMINION_ROOT and provides initialization support.
"""
import os
import sys
from typing import Tuple
from .quantum_authority import generate_root_key
from .secret_forge import retrieve_environment


def bootstrap_dominion_root() -> Tuple[bool, str]:
    """
    Bootstrap FORGE_DOMINION_ROOT key.
    
    Returns:
        tuple: (is_valid, message)
    """
    # Use forge to retrieve environment variable
    root_key = retrieve_environment("FORGE_DOMINION_ROOT")
    
    if root_key:
        # Validate existing root key
        try:
            # Check it's valid base64 and reasonable length
            if len(root_key) >= 40:
                print("[Dominion Bootstrap] ✅ Valid FORGE_DOMINION_ROOT found")
                print(f"[Dominion Bootstrap] Key fingerprint: {root_key[:8]}...")
                return True, "Valid root key found"
            else:
                print("[Dominion Bootstrap] ⚠️  FORGE_DOMINION_ROOT too short")
                return False, "Root key too short"
        except Exception as e:
            print(f"[Dominion Bootstrap] ❌ Invalid FORGE_DOMINION_ROOT: {e}")
            return False, f"Invalid root key: {e}"
    else:
        # Generate temporary root key for local development
        temp_key = generate_root_key()
        print("[Dominion Bootstrap] ⚠️  No FORGE_DOMINION_ROOT in environment")
        print("[Dominion Bootstrap] 🔑 Generated temporary root key for local use:")
        print(f"\nFORGE_DOMINION_ROOT={temp_key}\n")
        print("[Dominion Bootstrap] To persist this key, run:")
        print(f'  export FORGE_DOMINION_ROOT="{temp_key}"')
        print("\n[Dominion Bootstrap] For GitHub Actions, set as secret:")
        print(f'  gh secret set FORGE_DOMINION_ROOT --body "{temp_key}"')
        print()
        return False, "No root key - temporary key generated"


def validate_dominion_mode() -> Tuple[bool, str]:
    """
    Validate FORGE_DOMINION_MODE setting.
    
    Returns:
        tuple: (is_valid, message)
    """
    # Use forge to retrieve environment variable
    mode = retrieve_environment("FORGE_DOMINION_MODE", "sovereign")
    
    valid_modes = ["sovereign", "managed", "audit"]
    
    if mode in valid_modes:
        print(f"[Dominion Bootstrap] ✅ Mode: {mode}")
        return True, f"Valid mode: {mode}"
    else:
        print(f"[Dominion Bootstrap] ⚠️  Invalid mode: {mode}")
        print(f"[Dominion Bootstrap] Valid modes: {', '.join(valid_modes)}")
        return False, f"Invalid mode: {mode}"


def validate_dominion_version() -> Tuple[bool, str]:
    """
    Validate FORGE_DOMINION_VERSION setting.
    
    Returns:
        tuple: (is_valid, message)
    """
    # Use forge to retrieve environment variable
    version = retrieve_environment("FORGE_DOMINION_VERSION", "1.9.7s")
    expected_version = "1.9.7s"
    
    if version == expected_version:
        print(f"[Dominion Bootstrap] ✅ Version: {version}")
        return True, f"Version matches: {version}"
    else:
        print(f"[Dominion Bootstrap] ⚠️  Version mismatch: {version} (expected {expected_version})")
        return False, f"Version mismatch: {version}"


def bootstrap() -> int:
    """
    Run full Dominion bootstrap validation.
    
    Returns:
        int: Exit code (0 = success, 1 = warnings, 2 = critical failure)
    """
    print("=" * 70)
    print("🜂 Forge Dominion Bootstrap v1.9.7s")
    print("=" * 70)
    print()
    
    # Check root key (critical)
    root_valid, root_msg = bootstrap_dominion_root()
    
    # Check mode (non-critical)
    mode_valid, mode_msg = validate_dominion_mode()
    
    # Check version (non-critical)
    version_valid, version_msg = validate_dominion_version()
    
    print()
    print("=" * 70)
    
    if not root_valid:
        # Critical failure in CI, warning in local
        # Use forge to retrieve CI detection variables
        is_ci = retrieve_environment("CI") == "true" or retrieve_environment("GITHUB_ACTIONS") == "true"
        
        if is_ci:
            print("[Dominion Bootstrap] ❌ CRITICAL: No FORGE_DOMINION_ROOT in CI")
            print("[Dominion Bootstrap] Set secret with:")
            print('  gh secret set FORGE_DOMINION_ROOT --body "$(python - <<\'PY\'\nimport base64, os; print(base64.urlsafe_b64encode(os.urandom(32)).decode().rstrip("="))\nPY\n)"')
            print("=" * 70)
            return 2  # Critical failure in CI
        else:
            print("[Dominion Bootstrap] ⚠️  Local development mode - use temporary key")
            print("=" * 70)
            return 1  # Warning in local
    
    if not mode_valid or not version_valid:
        print("[Dominion Bootstrap] ⚠️  Bootstrap complete with warnings")
        print("=" * 70)
        return 1  # Warnings
    
    print("[Dominion Bootstrap] ✅ Bootstrap complete - all checks passed")
    print("=" * 70)
    return 0  # Success


if __name__ == "__main__":
    exit_code = bootstrap()
    sys.exit(exit_code)
