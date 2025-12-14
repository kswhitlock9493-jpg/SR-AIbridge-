#!/usr/bin/env python3
"""
Demonstration script for Token Metadata Validation Security Patch

This script demonstrates the new metadata validation functionality
that addresses the security gap in token creation.
"""

import os
import sys
import time
from datetime import datetime, timezone

# Add the parent directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from bridge_backend.bridge_core.token_forge_dominion import (
    generate_ephemeral_token,
    validate_ephemeral_token,
    get_token_metadata,
    MetadataValidationError,
    reset_forge
)


def print_section(title):
    """Print a section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def demo_without_enforcement():
    """Demonstrate token creation without metadata enforcement."""
    print_section("Demo 1: Token Creation WITHOUT Enforcement (Backward Compatible)")
    
    # Ensure SOVEREIGN_GIT is not set
    os.environ.pop("SOVEREIGN_GIT", None)
    reset_forge()
    
    print("Creating token WITHOUT metadata...")
    token = generate_ephemeral_token("demo_service", ttl=300)
    print(f"✅ Token created: {token[:50]}...")
    
    print("\nValidating token...")
    is_valid = validate_ephemeral_token(token)
    print(f"✅ Token is valid: {is_valid}")
    
    print("\nExtracting metadata...")
    metadata = get_token_metadata(token)
    print(f"ℹ️  Metadata: {metadata}")


def demo_with_valid_metadata():
    """Demonstrate token creation with valid metadata."""
    print_section("Demo 2: Token Creation WITH Valid Metadata")
    
    # Ensure SOVEREIGN_GIT is not set
    os.environ.pop("SOVEREIGN_GIT", None)
    reset_forge()
    
    metadata = {
        "creator_identity": "demo_user@example.com",
        "creation_timestamp": int(time.time()),
        "intended_purpose": "api_access",
        "expiration_policy": "5_minutes",
        "access_scope": "read_write",
        "audit_trail_id": f"audit_{int(time.time())}"
    }
    
    print("Creating token WITH valid metadata...")
    print(f"Metadata: {metadata}")
    
    token = generate_ephemeral_token("demo_service", ttl=300, metadata=metadata)
    print(f"\n✅ Token created: {token[:50]}...")
    
    print("\nValidating token...")
    is_valid = validate_ephemeral_token(token)
    print(f"✅ Token is valid: {is_valid}")
    
    print("\nExtracting metadata...")
    extracted = get_token_metadata(token)
    print(f"✅ Metadata extracted: {extracted}")
    print(f"   - Creator: {extracted['creator_identity']}")
    print(f"   - Purpose: {extracted['intended_purpose']}")
    print(f"   - Scope: {extracted['access_scope']}")
    print(f"   - Audit ID: {extracted['audit_trail_id']}")


def demo_with_enforcement():
    """Demonstrate token creation with SOVEREIGN_GIT enforcement."""
    print_section("Demo 3: Token Creation WITH Enforcement (SOVEREIGN_GIT=true)")
    
    # Enable enforcement
    os.environ["SOVEREIGN_GIT"] = "true"
    reset_forge()
    
    print("⚠️  SOVEREIGN_GIT=true - Metadata is REQUIRED\n")
    
    print("Attempting to create token WITHOUT metadata...")
    try:
        token = generate_ephemeral_token("demo_service", ttl=300)
        print("❌ This should not succeed!")
    except MetadataValidationError as e:
        print(f"✅ Token creation BLOCKED: {e}")
    
    print("\n" + "-" * 80 + "\n")
    
    metadata = {
        "creator_identity": "admin@example.com",
        "creation_timestamp": int(time.time()),
        "intended_purpose": "critical_operation",
        "expiration_policy": "10_minutes",
        "access_scope": "admin_access",
        "audit_trail_id": f"audit_{int(time.time())}"
    }
    
    print("Creating token WITH valid metadata...")
    token = generate_ephemeral_token("demo_service", ttl=300, metadata=metadata)
    print(f"✅ Token created: {token[:50]}...")
    
    print("\nValidating token...")
    is_valid = validate_ephemeral_token(token)
    print(f"✅ Token is valid: {is_valid}")


def demo_invalid_metadata():
    """Demonstrate validation of invalid metadata."""
    print_section("Demo 4: Security - Invalid Metadata Detection")
    
    # Enable enforcement
    os.environ["SOVEREIGN_GIT"] = "true"
    reset_forge()
    
    test_cases = [
        {
            "name": "Missing required fields",
            "metadata": {
                "creator_identity": "user@example.com",
                "creation_timestamp": int(time.time()),
            }
        },
        {
            "name": "Empty creator identity",
            "metadata": {
                "creator_identity": "",
                "creation_timestamp": int(time.time()),
                "intended_purpose": "test",
                "expiration_policy": "5min",
                "access_scope": "read",
                "audit_trail_id": "audit_123"
            }
        },
        {
            "name": "Invalid timestamp format",
            "metadata": {
                "creator_identity": "user@example.com",
                "creation_timestamp": "invalid_timestamp",
                "intended_purpose": "test",
                "expiration_policy": "5min",
                "access_scope": "read",
                "audit_trail_id": "audit_123"
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['name']}")
        print(f"Metadata: {test_case['metadata']}")
        
        try:
            token = generate_ephemeral_token("demo_service", ttl=300, metadata=test_case["metadata"])
            print("❌ Token creation should have been blocked!")
        except MetadataValidationError as e:
            print(f"✅ Validation BLOCKED: {str(e)[:100]}...")


def demo_security_summary():
    """Print security summary."""
    print_section("🛡️  Security Summary")
    
    print("BEFORE: Token Metadata Validation Patch")
    print("  ❌ Tokens could be created without metadata")
    print("  ❌ No validation of metadata fields")
    print("  ❌ Unauthorized tokens could bypass security")
    print("  ❌ No audit trail enforcement")
    
    print("\nAFTER: Token Metadata Validation Patch")
    print("  ✅ Metadata validation enforced when SOVEREIGN_GIT=true")
    print("  ✅ 6 required fields validated: creator_identity, creation_timestamp,")
    print("     intended_purpose, expiration_policy, access_scope, audit_trail_id")
    print("  ✅ Unauthorized tokens are rejected")
    print("  ✅ Complete audit trail for all tokens")
    print("  ✅ Backward compatible with existing tokens")
    
    print("\nActivation:")
    print("  1. Set SOVEREIGN_GIT=true in environment")
    print("  2. All new tokens will require valid metadata")
    print("  3. Existing tokens without metadata continue to work")
    
    print("\n" + "=" * 80)


def main():
    """Run all demonstrations."""
    # Set up test environment
    os.environ["FORGE_DOMINION_ROOT"] = "demo_forge_root_key_for_testing_12345678901234567890"
    
    print("\n" + "🔐" * 40)
    print("     TOKEN METADATA VALIDATION SECURITY PATCH DEMONSTRATION")
    print("🔐" * 40)
    
    try:
        demo_without_enforcement()
        demo_with_valid_metadata()
        demo_with_enforcement()
        demo_invalid_metadata()
        demo_security_summary()
        
        print("\n✅ All demonstrations completed successfully!\n")
        
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
