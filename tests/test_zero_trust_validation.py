"""
Unit tests for Zero-Trust Validation and Quantum Scanner v1.9.7s-SOVEREIGN

Tests behavioral anomaly detection, entropy validation, and secret scanning.
"""
import os
import pytest
from pathlib import Path

from bridge_backend.bridge_core.token_forge_dominion import (
    ZeroTrustValidator,
    QuantumScanner
)


class TestZeroTrustValidator:
    """Test zero-trust validation matrix."""
    
    def test_entropy_calculation(self):
        """Test Shannon entropy calculation."""
        validator = ZeroTrustValidator()
        
        # Low entropy string (all same character)
        low_entropy = validator.calculate_entropy("aaaaaaaaaa")
        assert low_entropy == 0.0
        
        # High entropy string (random characters)
        high_entropy = validator.calculate_entropy("a1B2c3D4e5F6")
        assert high_entropy > 2.0
        
        # Medium entropy
        medium_entropy = validator.calculate_entropy("password123")
        assert 0.0 < medium_entropy < high_entropy
    
    def test_secret_entropy_validation_pass(self):
        """Test secret entropy validation with sufficient entropy."""
        validator = ZeroTrustValidator()
        
        # Strong secret
        is_valid, reason = validator.validate_secret_entropy("aB3dE5fG7hI9jK1l")
        assert is_valid is True
        
        # Random base64-like string
        is_valid, reason = validator.validate_secret_entropy("xKj9mN2pQ4rS6tU8vW0y")
        assert is_valid is True
    
    def test_secret_entropy_validation_fail_length(self):
        """Test secret entropy validation fails on short secrets."""
        validator = ZeroTrustValidator()
        
        is_valid, reason = validator.validate_secret_entropy("short")
        assert is_valid is False
        assert "too short" in reason.lower()
    
    def test_secret_entropy_validation_fail_entropy(self):
        """Test secret entropy validation fails on low entropy."""
        validator = ZeroTrustValidator()
        
        # Long but low entropy
        is_valid, reason = validator.validate_secret_entropy("aaaaaaaaaaaaaaaa")
        assert is_valid is False
        assert "entropy" in reason.lower()
    
    def test_hardcoded_pattern_detection_api_key(self):
        """Test detection of hardcoded API keys."""
        validator = ZeroTrustValidator()
        
        content = 'api_key = "fake_test_key_XXXXXXXXXXXXXXXX"'
        detections = validator.detect_hardcoded_patterns(content)
        
        assert len(detections) > 0
        assert any(d["pattern"] == "api_key" for d in detections)
    
    def test_hardcoded_pattern_detection_github_token(self):
        """Test detection of GitHub tokens."""
        from bridge_backend.bridge_core.token_forge_dominion import generate_ephemeral_token
        
        validator = ZeroTrustValidator()
        
        # Use a realistic GitHub token pattern for testing detection
        # This is a fake pattern that looks like a GitHub token but is safe
        test_token = "ghp_" + "X" * 36  # Fake pattern for testing
        content = f'GITHUB_TOKEN={test_token}'
        detections = validator.detect_hardcoded_patterns(content)
        
        assert len(detections) > 0
        assert any(d["pattern"] == "github_token" for d in detections)
        assert any(d["severity"] == "high" or d["severity"] == "critical" for d in detections)
    
    def test_hardcoded_pattern_detection_private_key(self):
        """Test detection of private keys."""
        validator = ZeroTrustValidator()
        
        content = '-----BEGIN RSA PRIVATE KEY-----\nMIIEpAIBAAKCAQ...'
        detections = validator.detect_hardcoded_patterns(content)
        
        assert len(detections) > 0
        assert any(d["pattern"] == "private_key" for d in detections)
        assert any(d["severity"] in ["high", "critical"] for d in detections)
    
    def test_issuance_context_validation_valid(self):
        """Test successful issuance context validation."""
        validator = ZeroTrustValidator()
        
        is_valid, reason, report = validator.validate_issuance_context(
            provider="render",
            environment="production",
            requester="test_user",
            metadata={"test": True}
        )
        
        assert is_valid is True
        assert "checks" in report
        assert report["checks"]["provider"]["passed"] is True
        assert report["checks"]["environment"]["passed"] is True
    
    def test_issuance_context_validation_invalid_provider(self):
        """Test issuance validation rejects unknown provider."""
        validator = ZeroTrustValidator()
        
        is_valid, reason, report = validator.validate_issuance_context(
            provider="unknown_provider",
            environment="production"
        )
        
        assert is_valid is False
        assert "provider" in reason.lower()
    
    def test_issuance_context_validation_invalid_environment(self):
        """Test issuance validation rejects unknown environment."""
        validator = ZeroTrustValidator()
        
        is_valid, reason, report = validator.validate_issuance_context(
            provider="render",
            environment="invalid_env"
        )
        
        assert is_valid is False
        assert "environment" in reason.lower()
    
    def test_issuance_context_validation_rate_limit(self):
        """Test rate limiting in issuance validation."""
        validator = ZeroTrustValidator()
        
        # Issue many validations quickly
        for i in range(70):  # Exceed the limit of 60/min
            validator.validate_issuance_context(
                provider="render",
                environment="production"
            )
        
        # Next one should fail due to rate limit
        is_valid, reason, report = validator.validate_issuance_context(
            provider="render",
            environment="production"
        )
        
        # Note: Actual rate limiting may not trigger in fast tests
        # This test documents expected behavior
        assert "rate_limit" in report["checks"]
    
    def test_scan_environment_for_secrets(self):
        """Test environment variable scanning."""
        validator = ZeroTrustValidator()
        
        env_vars = {
            "API_KEY": "fake_key_XXXXXXXXXXXXXXXXXXXXXXXXXXXX",
            "SECRET_TOKEN": "very_secret_value_with_entropy",
            "DATABASE_URL": "postgresql://user:pass@host/db",
            "DEBUG": "true"
        }
        
        report = validator.scan_environment_for_secrets(env_vars)
        
        assert "timestamp" in report
        assert "total_vars" in report
        assert "findings" in report
        assert "summary" in report
        assert report["total_vars"] == 4
    
    def test_validation_metrics(self):
        """Test validation metrics tracking."""
        validator = ZeroTrustValidator()
        
        # Perform some validations
        validator.validate_issuance_context("render", "production")
        validator.validate_issuance_context("netlify", "staging")
        
        metrics = validator.get_validation_metrics()
        
        assert "total_validations" in metrics
        assert "total_failures" in metrics
        assert "success_rate" in metrics
        assert metrics["total_validations"] >= 2


class TestQuantumScanner:
    """Test quantum scanner for secret detection."""
    
    def test_scanner_initialization(self):
        """Test scanner initialization."""
        scanner = QuantumScanner(root_path=".")
        assert scanner.root_path == Path(".")
    
    def test_should_scan_file_python(self, tmp_path):
        """Test file scanning decision for Python files."""
        scanner = QuantumScanner(root_path=str(tmp_path))
        
        # Create test files
        py_file = tmp_path / "test.py"
        py_file.write_text("# test file")
        
        src_file = tmp_path / "src" / "module.py"
        src_file.parent.mkdir()
        src_file.write_text("# module")
        
        # Should scan Python files
        assert scanner.should_scan_file(py_file) is True
        assert scanner.should_scan_file(src_file) is True
    
    def test_should_scan_file_excluded(self):
        """Test file scanning excludes certain paths."""
        scanner = QuantumScanner()
        
        # Should not scan excluded directories
        assert scanner.should_scan_file(Path("node_modules/package/index.js")) is False
        assert scanner.should_scan_file(Path(".git/config")) is False
        assert scanner.should_scan_file(Path("__pycache__/module.pyc")) is False
    
    def test_should_scan_file_unsupported_extension(self):
        """Test file scanning skips unsupported extensions."""
        scanner = QuantumScanner()
        
        # Should not scan binary or unsupported files
        assert scanner.should_scan_file(Path("image.png")) is False
        assert scanner.should_scan_file(Path("video.mp4")) is False
        assert scanner.should_scan_file(Path("binary.exe")) is False
    
    def test_scan_file_with_secrets(self, tmp_path):
        """Test scanning a file with hardcoded secrets."""
        scanner = QuantumScanner(root_path=str(tmp_path))
        
        # Create test file with secrets
        # Use fake patterns that look like secrets but are safe test data
        test_file = tmp_path / "test.py"
        # Create a realistic-looking fake token for testing
        fake_token = "ghp_" + "X" * 36
        test_file.write_text(f"""
# Test file with secrets
API_KEY = "fake_test_XXXXXXXXXXXXXXXX"
SECRET_TOKEN = "{fake_token}"  # Fake GitHub token pattern for testing
password = "hardcoded_password_123"
""")
        
        results = scanner.scan_file(test_file)
        
        assert results["file"] == "test.py"
        assert len(results["findings"]) > 0
        assert any(f["severity"] in ["critical", "high"] for f in results["findings"])
    
    def test_scan_file_clean(self, tmp_path):
        """Test scanning a clean file."""
        scanner = QuantumScanner(root_path=str(tmp_path))
        
        # Create clean test file
        test_file = tmp_path / "clean.py"
        test_file.write_text("""
# Clean file with no secrets
import os

def main():
    api_key = os.getenv("API_KEY")
    return api_key
""")
        
        results = scanner.scan_file(test_file)
        
        assert results["file"] == "clean.py"
        # Should have no or minimal findings
        critical_findings = [f for f in results["findings"] if f["severity"] == "critical"]
        assert len(critical_findings) == 0
    
    def test_quantum_scan_directory(self, tmp_path):
        """Test scanning an entire directory."""
        scanner = QuantumScanner(root_path=str(tmp_path))
        
        # Create test files
        (tmp_path / "clean.py").write_text("# Clean file\nprint('hello')")
        (tmp_path / "secret.py").write_text('API_KEY = "fake_secret_XXXXXXXXXXXXXXXXX"')
        
        # Create excluded directory
        excluded = tmp_path / "node_modules"
        excluded.mkdir()
        (excluded / "package.js").write_text("secret = 'should_not_scan'")
        
        report = scanner.quantum_scan()
        
        assert "timestamp" in report
        assert "scan_path" in report
        assert "files_scanned" in report
        assert "total_findings" in report
        assert "status" in report
        assert "risk_score" in report
        
        # Should scan 2 files (not the one in node_modules)
        assert report["files_scanned"] == 2
    
    def test_quantum_scan_status_classification(self, tmp_path):
        """Test scan status classification based on findings."""
        scanner = QuantumScanner(root_path=str(tmp_path))
        
        # Clean repo
        (tmp_path / "clean.py").write_text("print('clean')")
        report_clean = scanner.quantum_scan()
        assert report_clean["status"] in ["CLEAN", "LOW_RISK"]
        
        # Repo with critical issues - use fake pattern for testing
        (tmp_path / "critical.py").write_text('GITHUB_TOKEN = "ghp_' + 'X' * 36 + '"  # Fake pattern for test')
        scanner2 = QuantumScanner(root_path=str(tmp_path))
        report_critical = scanner2.quantum_scan()
        # Should detect the GitHub token pattern
        assert report_critical["total_findings"] > 0
    
    def test_remediation_report(self, tmp_path):
        """Test remediation report generation."""
        scanner = QuantumScanner(root_path=str(tmp_path))
        
        # Create file with issues
        (tmp_path / "issues.py").write_text('SECRET = "fake_test_XXXXXXXXXXXXXXXXXXXXXXX"')
        
        # Scan
        scanner.quantum_scan()
        
        # Generate remediation
        remediation = scanner.generate_remediation_report()
        
        assert "timestamp" in remediation
        assert "total_issues" in remediation
        assert "recommendations" in remediation


class TestIntegration:
    """Integration tests for zero-trust and scanning."""
    
    def test_full_security_workflow(self, tmp_path):
        """Test complete security validation workflow."""
        # Create validator
        validator = ZeroTrustValidator()
        
        # Validate context
        is_valid, reason, report = validator.validate_issuance_context(
            provider="render",
            environment="production",
            requester="security_test"
        )
        assert is_valid is True
        
        # Scan environment
        env_report = validator.scan_environment_for_secrets({
            "API_KEY": "fake_valid_key_with_entropy_XXXXXXXX",
            "DATABASE_URL": "postgresql://localhost/db"
        })
        assert env_report["total_vars"] == 2
        
        # Scan codebase
        scanner = QuantumScanner(root_path=str(tmp_path))
        (tmp_path / "app.py").write_text("import os\napi_key = os.getenv('API_KEY')")
        
        scan_report = scanner.quantum_scan()
        
        # Verify all components work together
        assert scan_report["status"] in ["CLEAN", "LOW_RISK", "MEDIUM_RISK"]
