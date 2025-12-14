"""
Unit tests for Quantum Dominion Token Forge v1.9.7s-SOVEREIGN

Tests quantum authority, sovereign integration, and enterprise orchestrator.
"""
import os
import json
import pytest
from datetime import datetime, timedelta
from pathlib import Path

from bridge_backend.bridge_core.token_forge_dominion import (
    QuantumAuthority,
    SovereignIntegration,
    EnterpriseOrchestrator,
    generate_root_key
)


class TestQuantumAuthority:
    """Test quantum authority token minting and validation."""
    
    def test_root_key_generation(self):
        """Test root key generation produces valid base64."""
        root_key = generate_root_key()
        assert isinstance(root_key, str)
        assert len(root_key) >= 40  # Base64 of 32 bytes
        
    def test_authority_initialization(self):
        """Test quantum authority can be initialized."""
        authority = QuantumAuthority()
        assert authority.version == "1.9.7s"
        assert authority.mode == os.getenv("FORGE_DOMINION_MODE", "sovereign")
    
    def test_key_derivation(self):
        """Test HKDF-SHA384 key derivation."""
        authority = QuantumAuthority()
        
        context = "test-provider-v1"
        derived_key = authority.derive_key(context)
        
        assert isinstance(derived_key, bytes)
        assert len(derived_key) == 48  # 384 bits = 48 bytes
        
        # Same context with same salt should produce same key
        salt = b"fixed_salt_for_test"
        key1 = authority.derive_key(context, salt)
        key2 = authority.derive_key(context, salt)
        assert key1 == key2
        
        # Different context should produce different key
        key3 = authority.derive_key("different-context", salt)
        assert key1 != key3
    
    def test_token_minting(self):
        """Test quantum token minting."""
        authority = QuantumAuthority()
        
        token = authority.mint_quantum_token(
            provider="render",
            ttl_seconds=300,
            metadata={"test": True}
        )
        
        # Verify token structure
        assert "token" in token
        assert "signature" in token
        assert "nonce" in token
        assert "algorithm" in token
        assert token["algorithm"] == "HMAC-SHA384"
        assert token["key_derivation"] == "HKDF-SHA384"
        
        # Verify signature is hexadecimal
        assert len(token["signature"]) == 96  # SHA384 = 384 bits = 96 hex chars
        assert all(c in "0123456789abcdef" for c in token["signature"])
    
    def test_token_validation_success(self):
        """Test successful token validation."""
        authority = QuantumAuthority()
        
        # Mint a token
        token = authority.mint_quantum_token(
            provider="netlify",
            ttl_seconds=300
        )
        
        # Validate it
        is_valid, payload = authority.verify_token(token)
        
        assert is_valid is True
        assert payload is not None
        assert payload["provider"] == "netlify"
        assert payload["version"] == "1.9.7s"
    
    def test_token_validation_expired(self):
        """Test token validation rejects expired tokens."""
        authority = QuantumAuthority()
        
        # Mint a token with 0 second TTL
        token = authority.mint_quantum_token(
            provider="github",
            ttl_seconds=0
        )
        
        # Should be immediately invalid
        is_valid, payload = authority.verify_token(token)
        
        assert is_valid is False
        assert payload is None
    
    def test_token_validation_tampered_signature(self):
        """Test token validation rejects tampered signatures."""
        authority = QuantumAuthority()
        
        # Mint a valid token
        token = authority.mint_quantum_token(
            provider="render",
            ttl_seconds=300
        )
        
        # Tamper with signature
        tampered_token = token.copy()
        tampered_token["signature"] = "0" * 96
        
        # Should fail validation
        is_valid, payload = authority.verify_token(tampered_token)
        
        assert is_valid is False
        assert payload is None
    
    def test_key_fingerprint(self):
        """Test key fingerprint generation."""
        authority = QuantumAuthority()
        fingerprint = authority.get_key_fingerprint()
        
        assert isinstance(fingerprint, str)
        assert len(fingerprint) == 16
        assert all(c in "0123456789abcdef" for c in fingerprint)
    
    def test_key_rotation(self):
        """Test root key rotation."""
        authority = QuantumAuthority()
        
        old_fingerprint = authority.get_key_fingerprint()
        new_key = authority.rotate_root_key()
        new_fingerprint = authority.get_key_fingerprint()
        
        assert isinstance(new_key, str)
        assert old_fingerprint != new_fingerprint


class TestSovereignIntegration:
    """Test sovereign integration and resonance-aware security."""
    
    def test_initialization(self):
        """Test sovereign integration initialization."""
        integration = SovereignIntegration()
        assert integration.policies is not None
        assert "min_ttl_seconds" in integration.policies
    
    def test_resonance_classification(self):
        """Test resonance score classification."""
        integration = SovereignIntegration()
        
        assert integration.classify_resonance(20) == "critical"
        assert integration.classify_resonance(40) == "degraded"
        assert integration.classify_resonance(70) == "normal"
        assert integration.classify_resonance(90) == "optimal"
    
    def test_resonance_aware_ttl(self):
        """Test resonance-aware TTL calculation."""
        integration = SovereignIntegration()
        
        # Create mock state file with different resonance scores
        state_file = Path(".alik/test_forge_state.json")
        state_file.parent.mkdir(exist_ok=True)
        
        # Test with critical resonance
        with open(state_file, 'w') as f:
            json.dump({"resonance_score": 20, "health_status": "critical"}, f)
        
        integration_critical = SovereignIntegration(str(state_file))
        ttl_critical = integration_critical.get_resonance_aware_ttl(300, "render", "production")
        
        # Critical resonance should have short TTL (60-120s)
        assert 60 <= ttl_critical <= 120
        
        # Test with optimal resonance
        with open(state_file, 'w') as f:
            json.dump({"resonance_score": 90, "health_status": "optimal"}, f)
        
        integration_optimal = SovereignIntegration(str(state_file))
        ttl_optimal = integration_optimal.get_resonance_aware_ttl(300, "render", "production")
        
        # Optimal resonance should have longer TTL
        assert ttl_optimal >= ttl_critical
        
        # Cleanup
        state_file.unlink(missing_ok=True)
    
    def test_policy_guard(self):
        """Test sovereign policy guard enforcement."""
        integration = SovereignIntegration()
        
        # Test with valid context
        is_allowed, reason = integration.enforce_policy_guard(
            action="token_issuance",
            context={"validated": True, "environment": "production"}
        )
        assert is_allowed is True
        
        # Test with invalid context (not validated)
        is_allowed, reason = integration.enforce_policy_guard(
            action="token_issuance",
            context={"validated": False, "environment": "production"}
        )
        assert is_allowed is False
        assert "Zero-trust" in reason
    
    def test_sovereign_status(self):
        """Test sovereign status report."""
        integration = SovereignIntegration()
        status = integration.get_sovereign_status()
        
        assert "timestamp" in status
        assert "version" in status
        assert "resonance" in status
        assert "policies" in status
        assert status["version"] == "1.9.7s-SOVEREIGN"


class TestEnterpriseOrchestrator:
    """Test enterprise orchestrator for deployments."""
    
    def test_initialization(self):
        """Test orchestrator initialization."""
        orchestrator = EnterpriseOrchestrator(environment="staging")
        assert orchestrator.environment == "staging"
    
    def test_health_check(self):
        """Test health check functionality."""
        orchestrator = EnterpriseOrchestrator()
        health = orchestrator.health_check()
        
        assert "timestamp" in health
        assert "components" in health
        assert "overall_status" in health
        
        # Check required components
        assert "quantum_authority" in health["components"]
        assert "validator" in health["components"]
        assert "sovereign_integration" in health["components"]
    
    def test_pre_deployment_checks(self):
        """Test pre-deployment validation."""
        orchestrator = EnterpriseOrchestrator(environment="development")
        passed, report = orchestrator.pre_deployment_checks()
        
        assert "timestamp" in report
        assert "environment" in report
        assert "checks" in report
        
        # Should have environment check
        assert "environment" in report["checks"]
        assert report["checks"]["environment"]["passed"] is True
    
    def test_deployment_dry_run(self):
        """Test dry-run deployment."""
        orchestrator = EnterpriseOrchestrator(environment="staging")
        
        result = orchestrator.execute_sovereign_deployment(
            providers=["render", "netlify"],
            dry_run=True
        )
        
        assert "timestamp" in result
        assert "environment" in result
        assert "providers" in result
        assert "results" in result
        assert result["dry_run"] is True
    
    def test_compliance_report(self):
        """Test compliance report generation."""
        orchestrator = EnterpriseOrchestrator()
        report = orchestrator.generate_compliance_report()
        
        assert "timestamp" in report
        assert "version" in report
        assert "environment" in report
        assert "validation_metrics" in report
        assert "sovereign_status" in report
        assert report["version"] == "1.9.7s-SOVEREIGN"


class TestIntegration:
    """Integration tests for complete workflows."""
    
    def test_end_to_end_token_lifecycle(self):
        """Test complete token lifecycle from minting to validation."""
        # Initialize components
        authority = QuantumAuthority()
        integration = SovereignIntegration()
        
        # Mint token with resonance-aware TTL
        ttl = integration.get_resonance_aware_ttl(300, "render", "production")
        token = authority.mint_quantum_token(
            provider="render",
            ttl_seconds=ttl,
            metadata={"integration_test": True}
        )
        
        # Validate token
        is_valid, payload = authority.verify_token(token)
        
        assert is_valid is True
        assert payload["provider"] == "render"
        assert payload["metadata"]["integration_test"] is True
    
    def test_orchestrator_deployment_workflow(self):
        """Test full deployment workflow."""
        orchestrator = EnterpriseOrchestrator(environment="staging")
        
        # Run health check
        health = orchestrator.health_check()
        assert health["overall_status"] in ["healthy", "degraded"]
        
        # Run pre-deployment checks
        checks_passed, checks_report = orchestrator.pre_deployment_checks()
        
        # Execute deployment (dry run)
        deployment = orchestrator.execute_sovereign_deployment(
            providers=["render"],
            dry_run=True
        )
        
        assert "status" in deployment
        assert "results" in deployment
