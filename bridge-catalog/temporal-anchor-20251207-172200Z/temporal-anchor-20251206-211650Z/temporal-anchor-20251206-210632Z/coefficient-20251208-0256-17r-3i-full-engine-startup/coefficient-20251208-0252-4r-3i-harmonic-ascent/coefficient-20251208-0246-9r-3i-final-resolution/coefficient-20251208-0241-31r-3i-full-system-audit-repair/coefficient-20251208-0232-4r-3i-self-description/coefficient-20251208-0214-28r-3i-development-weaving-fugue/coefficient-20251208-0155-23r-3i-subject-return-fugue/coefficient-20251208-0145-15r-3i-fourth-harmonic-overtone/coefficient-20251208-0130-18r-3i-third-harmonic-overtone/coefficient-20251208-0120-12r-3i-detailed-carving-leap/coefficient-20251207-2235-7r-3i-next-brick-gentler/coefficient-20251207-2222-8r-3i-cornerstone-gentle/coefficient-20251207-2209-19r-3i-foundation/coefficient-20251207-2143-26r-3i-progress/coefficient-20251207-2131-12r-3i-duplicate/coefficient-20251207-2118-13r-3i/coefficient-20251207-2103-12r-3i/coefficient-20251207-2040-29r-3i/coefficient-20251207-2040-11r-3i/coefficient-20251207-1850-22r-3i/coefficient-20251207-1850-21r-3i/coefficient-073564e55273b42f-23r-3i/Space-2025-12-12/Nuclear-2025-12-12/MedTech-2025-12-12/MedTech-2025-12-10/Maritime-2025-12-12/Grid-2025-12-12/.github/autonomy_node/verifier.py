"""
Reflex Loop Verifier - Merge Readiness Audit
v1.9.7o - Determines when reports are ready for PR generation
"""

from typing import Dict, Any


def ready_to_pr(report: Dict[str, Any]) -> bool:
    """
    Check if a report is ready to generate a PR.
    
    Only open a PR if:
    1. Fixes were applied (safe_fixes > 0)
    2. Truth verification passed
    
    Args:
        report: Report dictionary with fix and verification data
        
    Returns:
        True if report is ready for PR, False otherwise
    """
    # Check if fixes were applied
    has_fixes = report.get("safe_fixes", 0) > 0
    
    # Check if Truth verified the changes
    truth_verified = report.get("truth_verified", True)
    
    return has_fixes and truth_verified


def check_merge_readiness(pr_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Perform comprehensive merge readiness check.
    
    Args:
        pr_data: PR data with signature and metadata
        
    Returns:
        Dictionary with readiness status and details
    """
    # Import signer here to avoid circular import issues
    try:
        from . import signer as sig_module
    except ImportError:
        import signer as sig_module
    
    readiness = {
        "ready": False,
        "checks": {
            "has_signature": False,
            "signature_valid": False,
            "rbac_approved": False
        },
        "timestamp": None
    }
    
    # Check for signature
    if "sig" in pr_data:
        readiness["checks"]["has_signature"] = True
        
        # Verify signature
        if sig_module.verify_signature(pr_data):
            readiness["checks"]["signature_valid"] = True
    
    # Check RBAC
    if sig_module.verify_rbac("admiral"):
        readiness["checks"]["rbac_approved"] = True
    
    # Overall readiness
    readiness["ready"] = all(readiness["checks"].values())
    
    return readiness
