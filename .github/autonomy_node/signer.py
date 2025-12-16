"""
Truth Engine Signature Module for Reflex Loop Protocol
v1.9.7o - Provides PR signing and RBAC validation
"""

import hashlib
import json
import os
from typing import Dict, Any


def sign(pr_body: str) -> Dict[str, Any]:
    """
    Sign a PR body with Truth Engine signature.
    
    Args:
        pr_body: The PR body text to sign
        
    Returns:
        Dictionary with title, body (including signature), and sig hash
    """
    # Generate signature hash from PR body
    sig = hashlib.sha256(pr_body.encode()).hexdigest()[:16]
    
    # Build signed envelope
    signed_data = {
        "title": f"EAN Reflex Update [{sig}]",
        "body": pr_body + f"\n\n---\n**Truth Signature:** `{sig}`",
        "sig": sig
    }
    
    return signed_data


def verify_rbac(role: str = "admiral") -> bool:
    """
    Verify RBAC permissions for PR operations.
    
    Args:
        role: Role to check (default: "admiral")
        
    Returns:
        True if role has permission, False otherwise
    """
    # Check if RBAC is enabled
    rbac_enabled = os.getenv("RBAC_ENABLED", "true").lower() == "true"
    
    if not rbac_enabled:
        return True
    
    # Admiral role always has permission
    allowed_roles = ["admiral", "captain"]
    return role.lower() in allowed_roles


def verify_signature(signed_data: Dict[str, Any]) -> bool:
    """
    Verify a Truth Engine signature.
    
    Args:
        signed_data: Dictionary with body and sig fields
        
    Returns:
        True if signature is valid, False otherwise
    """
    if "body" not in signed_data or "sig" not in signed_data:
        return False
    
    # Extract the original body (before the signature was appended)
    body = signed_data["body"]
    expected_sig = signed_data["sig"]
    
    # Remove the signature section from the body to get original
    if "\n\n---\n**Truth Signature:**" in body:
        original_body = body.split("\n\n---\n**Truth Signature:**")[0]
    else:
        original_body = body
    
    # Recalculate signature
    calculated_sig = hashlib.sha256(original_body.encode()).hexdigest()[:16]
    
    return calculated_sig == expected_sig
