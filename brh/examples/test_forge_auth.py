#!/usr/bin/env python3
"""
Test script for BRH forge authentication
"""
import os
import sys
import time

# Add repository root to path
repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, repo_root)

from brh.forge_auth import parse_forge_root, verify_seal, mint_ephemeral_token


def test_forge_auth():
    """Test the forge authentication flow"""
    
    # Check if FORGE_DOMINION_ROOT is set
    forge_root = os.getenv("FORGE_DOMINION_ROOT")
    if not forge_root:
        print("❌ FORGE_DOMINION_ROOT not set")
        print("\nTo set it, run:")
        print("  ./brh/examples/generate_forge_root.sh")
        return False
    
    print("✓ FORGE_DOMINION_ROOT found")
    print(f"  {forge_root[:50]}...")
    
    # Parse the forge root
    try:
        ctx = parse_forge_root()
        print("\n✓ Successfully parsed FORGE_DOMINION_ROOT")
        print(f"  Root: {ctx.root}")
        print(f"  Env: {ctx.env}")
        print(f"  Epoch: {ctx.epoch}")
        print(f"  Signature: {ctx.sig[:16]}...")
    except Exception as e:
        print(f"\n❌ Failed to parse FORGE_DOMINION_ROOT: {e}")
        return False
    
    # Check if DOMINION_SEAL is set
    seal = os.getenv("DOMINION_SEAL")
    if not seal:
        print("\n⚠️  DOMINION_SEAL not set")
        print("  Verification will be skipped in allow_unsigned mode")
    else:
        print("\n✓ DOMINION_SEAL found")
    
    # Verify the seal
    try:
        verify_seal(ctx)
        print("✓ Signature verified successfully")
    except RuntimeError as e:
        print(f"❌ Signature verification failed: {e}")
        return False
    
    # Check time skew
    now = int(time.time())
    skew = abs(now - ctx.epoch)
    print(f"\n✓ Time skew: {skew} seconds")
    if skew > 900:
        print("  ⚠️  Warning: Time skew is > 15 minutes")
    
    # Mint ephemeral token
    try:
        token = mint_ephemeral_token(ctx)
        print(f"\n✓ Ephemeral token minted")
        print(f"  Token: {token[:16]}... (truncated)")
    except Exception as e:
        print(f"\n❌ Failed to mint token: {e}")
        return False
    
    print("\n" + "="*50)
    print("✅ All forge authentication tests passed!")
    print("="*50)
    return True


if __name__ == "__main__":
    success = test_forge_auth()
    sys.exit(0 if success else 1)
