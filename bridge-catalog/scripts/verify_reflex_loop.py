#!/usr/bin/env python3
"""
Verification script for Reflex Loop Protocol v1.9.7o
Checks that all components are in place and working correctly
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

def check_module(module_path, description):
    """Check if a module can be imported"""
    try:
        sys.path.insert(0, os.path.dirname(module_path))
        module_name = os.path.basename(module_path).replace('.py', '')
        __import__(module_name)
        print(f"✓ {description}: {module_path}")
        return True
    except ImportError as e:
        print(f"✗ {description}: {module_path} ({e})")
        return False

def test_signer():
    """Test signer module functionality"""
    sys.path.insert(0, '.github/autonomy_node')
    try:
        import signer
        
        # Test signing
        pr_body = "Test PR body"
        signed = signer.sign(pr_body)
        assert "sig" in signed
        assert len(signed["sig"]) == 16
        
        # Test verification
        assert signer.verify_signature(signed) == True
        
        # Test RBAC
        assert signer.verify_rbac("admiral") == True
        assert signer.verify_rbac("guest") == False
        
        print("✓ Signer module: All tests passed")
        return True
    except Exception as e:
        print(f"✗ Signer module: {e}")
        return False

def test_verifier():
    """Test verifier module functionality"""
    sys.path.insert(0, '.github/autonomy_node')
    try:
        import verifier
        
        # Test ready_to_pr
        report_ready = {"safe_fixes": 3, "truth_verified": True}
        report_not_ready = {"safe_fixes": 0, "truth_verified": True}
        
        assert verifier.ready_to_pr(report_ready) == True
        assert verifier.ready_to_pr(report_not_ready) == False
        
        print("✓ Verifier module: All tests passed")
        return True
    except Exception as e:
        print(f"✗ Verifier module: {e}")
        return False

def main():
    print("=" * 60)
    print("Reflex Loop Protocol v1.9.7o Verification")
    print("=" * 60)
    print()
    
    checks = []
    
    # Core files
    print("Core Implementation Files:")
    checks.append(check_file(".github/autonomy_node/reflex.py", "Reflex Engine"))
    checks.append(check_file(".github/autonomy_node/signer.py", "Truth Signer"))
    checks.append(check_file(".github/autonomy_node/verifier.py", "Merge Verifier"))
    print()
    
    # Directories
    print("Directories:")
    checks.append(check_file(".github/autonomy_node/reports", "Reports Directory"))
    checks.append(check_file(".github/autonomy_node/pending_prs", "Pending PRs Directory"))
    checks.append(check_file(".github/autonomy_node/templates", "Templates Directory"))
    print()
    
    # Templates
    print("Templates:")
    checks.append(check_file(".github/autonomy_node/templates/pr_body.md", "PR Body Template"))
    print()
    
    # Workflow
    print("Workflow:")
    checks.append(check_file(".github/workflows/reflex_loop.yml", "Reflex Loop Workflow"))
    print()
    
    # Genesis Integration
    print("Genesis Integration:")
    checks.append(check_file("bridge_backend/genesis/activation.py", "Genesis Activation"))
    checks.append(check_file("bridge_backend/genesis/bus.py", "Genesis Bus"))
    print()
    
    # Documentation
    print("Documentation:")
    checks.append(check_file("docs/REFLEX_LOOP_PROTOCOL.md", "RLP Architecture"))
    checks.append(check_file("docs/AUTONOMY_PR_VERIFICATION.md", "PR Verification"))
    checks.append(check_file("docs/OFFLINE_QUEUE_HANDLING.md", "Offline Queue"))
    print()
    
    # Tests
    print("Tests:")
    checks.append(check_file("bridge_backend/tests/test_reflex_loop.py", "Test Suite"))
    print()
    
    # Functional tests
    print("Functional Tests:")
    checks.append(test_signer())
    checks.append(test_verifier())
    print()
    
    # Version check
    print("Version Check:")
    sys.path.insert(0, '.github/autonomy_node')
    try:
        import __init__ as autonomy_init
        version = autonomy_init.__version__
        if version == "1.9.7o":
            print(f"✓ Version: {version}")
            checks.append(True)
        else:
            print(f"✗ Version mismatch: {version} (expected 1.9.7o)")
            checks.append(False)
    except Exception as e:
        print(f"✗ Version check failed: {e}")
        checks.append(False)
    print()
    
    # Summary
    print("=" * 60)
    passed = sum(checks)
    total = len(checks)
    print(f"Summary: {passed}/{total} checks passed")
    
    if passed == total:
        print("✅ All components verified successfully!")
        print()
        print("🧠 Reflex Loop Protocol v1.9.7o is ready for operation!")
        return 0
    else:
        print("⚠️  Some components missing or have errors")
        return 1

if __name__ == "__main__":
    sys.exit(main())
