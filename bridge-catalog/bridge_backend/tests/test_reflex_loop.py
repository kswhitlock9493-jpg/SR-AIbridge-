"""
Test Reflex Loop Protocol
v1.9.7o - Comprehensive tests for autonomous PR generation
"""

import pytest
import json
import os
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timezone

# Import modules from autonomy_node
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../.github/autonomy_node'))

try:
    import signer
    import verifier
    import reflex
except ImportError as e:
    pytest.skip(f"Could not import autonomy_node modules: {e}", allow_module_level=True)


class TestSigner:
    """Test Truth Engine signing functionality"""
    
    def test_sign_creates_signature(self):
        """Verify signature is generated correctly"""
        pr_body = "Test PR body content"
        signed = signer.sign(pr_body)
        
        assert "title" in signed
        assert "body" in signed
        assert "sig" in signed
        assert len(signed["sig"]) == 16
        assert signed["sig"] in signed["title"]
        assert signed["sig"] in signed["body"]
    
    def test_signature_is_deterministic(self):
        """Same body should produce same signature"""
        pr_body = "Test PR body content"
        signed1 = signer.sign(pr_body)
        signed2 = signer.sign(pr_body)
        
        assert signed1["sig"] == signed2["sig"]
    
    def test_different_bodies_different_signatures(self):
        """Different bodies should produce different signatures"""
        signed1 = signer.sign("Body 1")
        signed2 = signer.sign("Body 2")
        
        assert signed1["sig"] != signed2["sig"]
    
    def test_verify_signature_valid(self):
        """Verify valid signature passes verification"""
        pr_body = "Test PR body content"
        signed = signer.sign(pr_body)
        
        assert signer.verify_signature(signed) == True
    
    def test_verify_signature_tampered_body(self):
        """Verify tampered body fails verification"""
        pr_body = "Test PR body content"
        signed = signer.sign(pr_body)
        
        # Tamper with the body
        signed["body"] = signed["body"].replace("Test", "Modified")
        
        assert signer.verify_signature(signed) == False
    
    def test_verify_signature_missing_fields(self):
        """Verify missing fields fail verification"""
        assert signer.verify_signature({}) == False
        assert signer.verify_signature({"body": "test"}) == False
        assert signer.verify_signature({"sig": "abc123"}) == False
    
    def test_verify_rbac_admiral(self):
        """Verify Admiral role has permission"""
        assert signer.verify_rbac("admiral") == True
        assert signer.verify_rbac("Admiral") == True
        assert signer.verify_rbac("ADMIRAL") == True
    
    def test_verify_rbac_captain(self):
        """Verify Captain role has permission"""
        assert signer.verify_rbac("captain") == True
        assert signer.verify_rbac("Captain") == True
    
    def test_verify_rbac_unauthorized(self):
        """Verify unauthorized roles are rejected"""
        assert signer.verify_rbac("guest") == False
        assert signer.verify_rbac("user") == False
        assert signer.verify_rbac("") == False


class TestVerifier:
    """Test merge readiness verification"""
    
    def test_ready_to_pr_with_fixes_and_verification(self):
        """Report with fixes and verification is ready"""
        report = {
            "safe_fixes": 3,
            "truth_verified": True
        }
        assert verifier.ready_to_pr(report) == True
    
    def test_ready_to_pr_no_fixes(self):
        """Report with no fixes is not ready"""
        report = {
            "safe_fixes": 0,
            "truth_verified": True
        }
        assert verifier.ready_to_pr(report) == False
    
    def test_ready_to_pr_not_verified(self):
        """Report without verification is not ready"""
        report = {
            "safe_fixes": 3,
            "truth_verified": False
        }
        assert verifier.ready_to_pr(report) == False
    
    def test_ready_to_pr_missing_fields(self):
        """Report with missing fields uses defaults"""
        report = {}
        assert verifier.ready_to_pr(report) == False
    
    def test_check_merge_readiness_all_pass(self):
        """All checks passing results in ready=True"""
        pr_body = "Test PR"
        signed = signer.sign(pr_body)
        
        readiness = verifier.check_merge_readiness(signed)
        
        assert readiness["ready"] == True
        assert readiness["checks"]["has_signature"] == True
        assert readiness["checks"]["signature_valid"] == True
        assert readiness["checks"]["rbac_approved"] == True
    
    def test_check_merge_readiness_no_signature(self):
        """Missing signature results in ready=False"""
        pr_data = {"title": "Test", "body": "Test"}
        
        readiness = verifier.check_merge_readiness(pr_data)
        
        assert readiness["ready"] == False
        assert readiness["checks"]["has_signature"] == False
    
    def test_check_merge_readiness_invalid_signature(self):
        """Invalid signature results in ready=False"""
        pr_data = {
            "title": "Test",
            "body": "Test",
            "sig": "invalid"
        }
        
        readiness = verifier.check_merge_readiness(pr_data)
        
        assert readiness["ready"] == False
        assert readiness["checks"]["signature_valid"] == False


class TestReflex:
    """Test Reflex Loop main functionality"""
    
    def setup_method(self):
        """Create temporary directories for testing"""
        self.test_dir = tempfile.mkdtemp()
        self.reports_dir = os.path.join(self.test_dir, "reports")
        self.pending_dir = os.path.join(self.test_dir, "pending_prs")
        os.makedirs(self.reports_dir, exist_ok=True)
        
        # Temporarily override directories in reflex module
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
    
    def teardown_method(self):
        """Clean up temporary directories"""
        os.chdir(self.original_cwd)
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_build_pr_body(self):
        """Verify PR body is built correctly"""
        report = {
            "summary": "Test issue detected",
            "safe_fixes": 5,
            "verified": True,
            "details": "Fixed configuration issues"
        }
        
        body = reflex.build_pr_body(report)
        
        assert "🤖 EAN Reflex PR" in body
        assert "Test issue detected" in body
        assert "5 files cleaned" in body
        assert "True verification status" in body
        assert "Fixed configuration issues" in body
    
    def test_build_pr_body_minimal_report(self):
        """Verify PR body works with minimal report"""
        report = {}
        
        body = reflex.build_pr_body(report)
        
        assert "🤖 EAN Reflex PR" in body
        assert "N/A" in body
        assert "0 files cleaned" in body
    
    def test_queue_offline(self):
        """Verify offline queueing works"""
        pr_data = {
            "title": "Test PR",
            "body": "Test body",
            "sig": "abc123"
        }
        
        # Create .github/autonomy_node structure
        os.makedirs(".github/autonomy_node", exist_ok=True)
        
        reflex.queue_offline(pr_data)
        
        # Check file was created
        pending_dir = ".github/autonomy_node/pending_prs"
        assert os.path.exists(pending_dir)
        
        files = [f for f in os.listdir(pending_dir) if f.endswith(".json")]
        assert len(files) == 1
        
        # Verify content
        with open(os.path.join(pending_dir, files[0]), 'r') as f:
            queued_data = json.load(f)
        
        assert queued_data["title"] == pr_data["title"]
        assert queued_data["body"] == pr_data["body"]
        assert queued_data["sig"] == pr_data["sig"]
    
    def test_reflex_loop_no_reports(self):
        """Verify reflex loop handles empty reports directory"""
        # Create .github/autonomy_node structure
        os.makedirs(".github/autonomy_node/reports", exist_ok=True)
        
        # Should not raise an error
        try:
            reflex.reflex_loop()
        except Exception as e:
            pytest.fail(f"reflex_loop raised unexpected exception: {e}")
    
    def test_reflex_loop_with_ready_report(self):
        """Verify reflex loop processes ready reports"""
        # Create .github/autonomy_node structure
        os.makedirs(".github/autonomy_node/reports", exist_ok=True)
        
        # Create a ready report
        report = {
            "summary": "Test issue",
            "safe_fixes": 3,
            "truth_verified": True,
            "details": "Fixed test issue"
        }
        
        report_file = ".github/autonomy_node/reports/test_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f)
        
        # Run reflex loop
        reflex.reflex_loop()
        
        # Verify PR was queued
        pending_dir = ".github/autonomy_node/pending_prs"
        assert os.path.exists(pending_dir)
        
        files = [f for f in os.listdir(pending_dir) if f.endswith(".json")]
        assert len(files) > 0
    
    def test_reflex_loop_with_not_ready_report(self):
        """Verify reflex loop skips not-ready reports"""
        # Create .github/autonomy_node structure
        os.makedirs(".github/autonomy_node/reports", exist_ok=True)
        
        # Create a not-ready report (no fixes)
        report = {
            "summary": "Test issue",
            "safe_fixes": 0,
            "truth_verified": True
        }
        
        report_file = ".github/autonomy_node/reports/test_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f)
        
        # Run reflex loop
        reflex.reflex_loop()
        
        # Verify no PR was queued
        pending_dir = ".github/autonomy_node/pending_prs"
        if os.path.exists(pending_dir):
            files = [f for f in os.listdir(pending_dir) if f.endswith(".json")]
            assert len(files) == 0


class TestIntegration:
    """End-to-end integration tests"""
    
    def setup_method(self):
        """Create temporary test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
    
    def teardown_method(self):
        """Clean up test environment"""
        os.chdir(self.original_cwd)
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_full_reflex_cycle(self):
        """Test complete reflex cycle from report to queued PR"""
        # Setup directory structure
        os.makedirs(".github/autonomy_node/reports", exist_ok=True)
        
        # Create report
        report = {
            "summary": "Configuration drift detected",
            "safe_fixes": 4,
            "truth_verified": True,
            "details": "Updated environment variables to match production"
        }
        
        report_file = ".github/autonomy_node/reports/config_drift.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Run reflex loop
        reflex.reflex_loop()
        
        # Verify PR was queued
        pending_dir = ".github/autonomy_node/pending_prs"
        assert os.path.exists(pending_dir)
        
        queued_files = [f for f in os.listdir(pending_dir) if f.endswith(".json")]
        assert len(queued_files) == 1
        
        # Load and verify queued PR
        with open(os.path.join(pending_dir, queued_files[0]), 'r') as f:
            pr_data = json.load(f)
        
        # Check PR data structure
        assert "title" in pr_data
        assert "body" in pr_data
        assert "sig" in pr_data
        
        # Verify signature in title
        assert pr_data["sig"] in pr_data["title"]
        
        # Verify body content
        assert "Configuration drift detected" in pr_data["body"]
        assert "4 files cleaned" in pr_data["body"]
        
        # Verify signature
        assert signer.verify_signature(pr_data) == True
        
        # Verify merge readiness
        readiness = verifier.check_merge_readiness(pr_data)
        assert readiness["ready"] == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
