#!/usr/bin/env python3
"""
Bridge Deploy Path Verification
Verifies deployment path coherence and readiness
"""
import sys
import os
import argparse
from pathlib import Path


def verify_deployment_paths():
    """
    Verify that critical deployment paths exist and are coherent.
    
    Returns:
        0 on success, 1 on failure
    """
    print("🌐 Checking deploy path coherence...")
    
    repo_root = Path(__file__).parent.parent.parent
    
    # Critical paths to verify
    critical_paths = [
        "bridge_backend",
        "bridge-frontend",
        "requirements.txt",
        ".github/workflows",
    ]
    
    all_paths_valid = True
    
    for path_str in critical_paths:
        path = repo_root / path_str
        if path.exists():
            print(f"  ✅ {path_str}")
        else:
            print(f"  ❌ Missing: {path_str}")
            all_paths_valid = False
    
    if all_paths_valid:
        print("✅ Path verification passed")
        return 0
    else:
        print("❌ Path verification failed - missing critical paths")
        return 1


def main():
    parser = argparse.ArgumentParser(description="Bridge Deploy Path Verification")
    parser.add_argument("--verify", action="store_true", help="Verify deployment paths")
    args = parser.parse_args()
    
    if args.verify:
        sys.exit(verify_deployment_paths())
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
