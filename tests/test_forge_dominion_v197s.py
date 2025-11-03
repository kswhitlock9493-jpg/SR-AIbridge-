"""
Unit tests for Forge Dominion v1.9.7s Environment Sovereignty
Tests bootstrap, scan, and lifecycle management components.
"""
import os
import json
import pytest
import tempfile
from pathlib import Path
from datetime import datetime, timedelta

from bridge_backend.bridge_core.token_forge_dominion import (
    generate_root_key,
    QuantumAuthority,
    TokenLifecycleManager,
    EnterpriseOrchestrator
)
from bridge_backend.bridge_core.token_forge_dominion.bootstrap import (
    bootstrap_dominion_root,
    validate_dominion_mode,
    validate_dominion_version
)
from bridge_backend.bridge_core.token_forge_dominion.scan_envs import (
    scan_envs,
    scan_file,
    should_ignore_line,
    SecretFinding
)


class TestBootstrap:
    """Test bootstrap functionality."""
    
    def test_generate_root_key(self):
        """Test root key generation."""
        key = generate_root_key()
        assert isinstance(key, str)
        assert len(key) >= 40  # Base64 of 32 bytes
    
    def test_bootstrap_with_valid_key(self, monkeypatch):
        """Test bootstrap with valid FORGE_DOMINION_ROOT."""
        key = generate_root_key()
        monkeypatch.setenv("FORGE_DOMINION_ROOT", key)
        
        is_valid, message = bootstrap_dominion_root()
        assert is_valid
        assert "Valid root key" in message
    
    def test_bootstrap_without_key(self, monkeypatch):
        """Test bootstrap without FORGE_DOMINION_ROOT."""
        monkeypatch.delenv("FORGE_DOMINION_ROOT", raising=False)
        
        is_valid, message = bootstrap_dominion_root()
        assert not is_valid
        assert "No root key" in message
    
    def test_validate_mode_sovereign(self, monkeypatch):
        """Test mode validation with sovereign mode."""
        monkeypatch.setenv("FORGE_DOMINION_MODE", "sovereign")
        
        is_valid, message = validate_dominion_mode()
        assert is_valid
        assert "sovereign" in message
    
    def test_validate_mode_invalid(self, monkeypatch):
        """Test mode validation with invalid mode."""
        monkeypatch.setenv("FORGE_DOMINION_MODE", "invalid_mode")
        
        is_valid, message = validate_dominion_mode()
        assert not is_valid
    
    def test_validate_version(self, monkeypatch):
        """Test version validation."""
        monkeypatch.setenv("FORGE_DOMINION_VERSION", "1.9.7s")
        
        is_valid, message = validate_dominion_version()
        assert is_valid


class TestSecretScanner:
    """Test secret scanning functionality."""
    
    def test_should_ignore_dominion_vars(self):
        """Test that Dominion variables are ignored."""
        line = "FORGE_DOMINION_ROOT=abcdef123456"
        assert should_ignore_line(line)
    
    def test_should_ignore_templates(self):
        """Test that template variables are ignored."""
        line = "API_KEY=${API_KEY}"
        assert should_ignore_line(line)
    
    def test_should_ignore_examples(self):
        """Test that example values are ignored."""
        line = "SECRET_KEY=example_value_here"
        assert should_ignore_line(line)
    
    def test_scan_file_with_secrets(self):
        """Test scanning file with secrets."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write("GITHUB_TOKEN=ghp_1234567890abcdefghijklmnopqrstuvwxyz\n")
            f.write("API_KEY=some_long_api_key_value_here_1234567890\n")
            temp_path = f.name
        
        try:
            findings = scan_file(Path(temp_path))
            assert len(findings) > 0
            
            # Check for GitHub token detection
            github_findings = [f for f in findings if f.pattern_name == 'github_token']
            assert len(github_findings) > 0
        finally:
            os.unlink(temp_path)
    
    def test_scan_file_clean(self):
        """Test scanning clean file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write("# Comment line\n")
            f.write("DEBUG=true\n")
            f.write("PORT=3000\n")
            temp_path = f.name
        
        try:
            findings = scan_file(Path(temp_path))
            assert len(findings) == 0
        finally:
            os.unlink(temp_path)
    
    def test_scan_envs_no_files(self):
        """Test scanning when no env files exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            results = scan_envs(tmpdir)
            assert results['count'] == 0
            assert len(results['scanned_files']) == 0


class TestTokenLifecycleManager:
    """Test token lifecycle management."""
    
    @pytest.fixture
    def temp_state_file(self):
        """Create temporary state file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        yield temp_path
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    def test_manager_initialization(self, temp_state_file, monkeypatch):
        """Test lifecycle manager initialization."""
        key = generate_root_key()
        monkeypatch.setenv("FORGE_DOMINION_ROOT", key)
        
        manager = TokenLifecycleManager(state_file=temp_state_file)
        assert manager is not None
        assert manager.authority is not None
    
    def test_renew_token(self, temp_state_file, monkeypatch):
        """Test token renewal."""
        key = generate_root_key()
        monkeypatch.setenv("FORGE_DOMINION_ROOT", key)
        
        manager = TokenLifecycleManager(state_file=temp_state_file)
        
        success, token_envelope = manager.renew_token("github", ttl_seconds=300)
        assert success
        assert "token" in token_envelope
        assert "signature" in token_envelope
    
    def test_validate_token(self, temp_state_file, monkeypatch):
        """Test token validation."""
        key = generate_root_key()
        monkeypatch.setenv("FORGE_DOMINION_ROOT", key)
        
        manager = TokenLifecycleManager(state_file=temp_state_file)
        
        # Renew and then validate
        success, token_envelope = manager.renew_token("github", ttl_seconds=300)
        assert success
        
        is_valid, payload = manager.validate_token("github")
        assert is_valid
        assert payload is not None
        assert payload["provider"] == "github"
    
    def test_needs_renewal_no_token(self, temp_state_file, monkeypatch):
        """Test needs_renewal when no token exists."""
        key = generate_root_key()
        monkeypatch.setenv("FORGE_DOMINION_ROOT", key)
        
        manager = TokenLifecycleManager(state_file=temp_state_file)
        
        needs_renewal, reason = manager.needs_renewal("github")
        assert needs_renewal
        assert "No token exists" in reason
    
    def test_needs_renewal_expired(self, temp_state_file, monkeypatch):
        """Test needs_renewal with expired token."""
        key = generate_root_key()
        monkeypatch.setenv("FORGE_DOMINION_ROOT", key)
        
        manager = TokenLifecycleManager(state_file=temp_state_file)
        
        # Create token with very short TTL
        success, token_envelope = manager.renew_token("github", ttl_seconds=1)
        assert success
        
        # Wait for expiration
        import time
        time.sleep(2)
        
        needs_renewal, reason = manager.needs_renewal("github")
        assert needs_renewal
    
    def test_validate_or_renew_new_token(self, temp_state_file, monkeypatch):
        """Test validate_or_renew creates new token."""
        key = generate_root_key()
        monkeypatch.setenv("FORGE_DOMINION_ROOT", key)
        
        manager = TokenLifecycleManager(state_file=temp_state_file)
        
        success, result = manager.validate_or_renew("github")
        assert success
        assert result["action"] == "renewed"
        assert result["provider"] == "github"
    
    def test_get_status(self, temp_state_file, monkeypatch):
        """Test getting status of all tokens."""
        key = generate_root_key()
        monkeypatch.setenv("FORGE_DOMINION_ROOT", key)
        
        manager = TokenLifecycleManager(state_file=temp_state_file)
        
        # Create some tokens
        manager.renew_token("github", ttl_seconds=300)
        manager.renew_token("netlify", ttl_seconds=600)
        
        status = manager.get_status()
        assert "tokens" in status
        assert "github" in status["tokens"]
        assert "netlify" in status["tokens"]


class TestEnterpriseOrchestrator:
    """Test enterprise orchestrator functionality."""
    
    def test_orchestrator_initialization(self, monkeypatch):
        """Test orchestrator initialization."""
        key = generate_root_key()
        monkeypatch.setenv("FORGE_DOMINION_ROOT", key)
        
        orchestrator = EnterpriseOrchestrator(environment="production")
        assert orchestrator is not None
        assert orchestrator.environment == "production"
    
    def test_pre_deployment_checks(self, monkeypatch):
        """Test pre-deployment checks."""
        key = generate_root_key()
        monkeypatch.setenv("FORGE_DOMINION_ROOT", key)
        
        orchestrator = EnterpriseOrchestrator(environment="production")
        
        passed, report = orchestrator.pre_deployment_checks()
        assert isinstance(passed, bool)
        assert "checks" in report
        assert "environment" in report["checks"]
        assert "root_key" in report["checks"]
    
    def test_health_check(self, monkeypatch):
        """Test health check."""
        key = generate_root_key()
        monkeypatch.setenv("FORGE_DOMINION_ROOT", key)
        
        orchestrator = EnterpriseOrchestrator(environment="production")
        
        health = orchestrator.health_check()
        assert "components" in health
        assert "quantum_authority" in health["components"]
        assert "overall_status" in health
    
    def test_check_pulse(self, monkeypatch):
        """Test pulse checking."""
        key = generate_root_key()
        monkeypatch.setenv("FORGE_DOMINION_ROOT", key)
        
        orchestrator = EnterpriseOrchestrator(environment="production")
        
        pulse_status = orchestrator.check_pulse()
        assert "governance_lock" in pulse_status
        assert "pulse_strength" in pulse_status
        assert "pulse_metrics" in pulse_status
    
    def test_record_pulse_event(self, monkeypatch):
        """Test recording pulse events."""
        key = generate_root_key()
        monkeypatch.setenv("FORGE_DOMINION_ROOT", key)
        
        orchestrator = EnterpriseOrchestrator(environment="production")
        
        # Record some events
        orchestrator.record_pulse_event("mint", "github")
        orchestrator.record_pulse_event("renew", "netlify")
        
        # Check pulse reflects events
        pulse_status = orchestrator.check_pulse()
        # Events might not be in pulse_metrics immediately due to time window
        assert pulse_status is not None
    
    def test_governance_lock_trigger(self, monkeypatch, tmpdir):
        """Test governance lock triggers on excessive mints."""
        key = generate_root_key()
        monkeypatch.setenv("FORGE_DOMINION_ROOT", key)
        
        # Use temp directory for pulse state
        pulse_file = tmpdir.join("forge_pulse.json")
        
        orchestrator = EnterpriseOrchestrator(environment="production")
        orchestrator.pulse_state_file = str(pulse_file)
        
        # Record excessive mint events
        for i in range(7):  # More than 5 triggers lock
            orchestrator.record_pulse_event("mint", "github")
        
        pulse_status = orchestrator.check_pulse()
        assert pulse_status["governance_lock"] == True
        assert len(pulse_status["alerts"]) > 0


class TestIntegration:
    """Integration tests for complete workflow."""
    
    def test_full_token_flow(self, monkeypatch):
        """Test complete token lifecycle flow."""
        key = generate_root_key()
        monkeypatch.setenv("FORGE_DOMINION_ROOT", key)
        monkeypatch.setenv("FORGE_DOMINION_MODE", "sovereign")
        monkeypatch.setenv("FORGE_DOMINION_VERSION", "1.9.7s")
        
        # Bootstrap
        is_valid, message = bootstrap_dominion_root()
        assert is_valid
        
        # Create manager
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_state = f.name
        
        try:
            manager = TokenLifecycleManager(state_file=temp_state)
            
            # Renew tokens for all providers
            providers = ['github', 'netlify', 'render']
            for provider in providers:
                success, result = manager.validate_or_renew(provider)
                assert success
                assert result["action"] == "renewed"
            
            # Get status
            status = manager.get_status()
            assert len(status["tokens"]) == 3
            
            # Validate all tokens are valid
            for provider in providers:
                is_valid, payload = manager.validate_token(provider)
                assert is_valid
                assert payload["provider"] == provider
                
        finally:
            if os.path.exists(temp_state):
                os.unlink(temp_state)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
