"""
Test Sovereign Compliance Guard
"""

import pytest
from datetime import datetime, UTC
from bridge_backend.bridge_engines.sovereign_guard import (
    SovereignComplianceGuard,
    ComplianceResult,
    AuditEntry
)


class TestSovereignComplianceGuard:
    """Test the Sovereign Compliance Guard"""
    
    def test_guard_initialization(self):
        """Test guard initializes with correct defaults"""
        guard = SovereignComplianceGuard()
        assert guard.min_resonance == 0.95
        assert guard.license_key is not None
        assert len(guard._audit_trail) == 0
    
    def test_license_validation(self):
        """Test quantum-resistant license validation"""
        guard = SovereignComplianceGuard()
        result = guard._validate_license_quantum("test_operation")
        assert isinstance(result, bool)
    
    def test_compliance_check_success(self):
        """Test successful compliance check"""
        guard = SovereignComplianceGuard()
        result = guard.check_compliance("test_operation")
        
        assert isinstance(result, ComplianceResult)
        assert result.timestamp is not None
        assert isinstance(result.compliant, bool)
        assert isinstance(result.license_valid, bool)
        assert isinstance(result.resonance_sufficient, bool)
        assert isinstance(result.policy_enforced, bool)
        assert isinstance(result.violations, list)
    
    def test_compliance_check_with_route(self):
        """Test compliance check with route validation"""
        guard = SovereignComplianceGuard()
        result = guard.check_compliance("test_operation", "/bridge/engines/status")
        
        assert isinstance(result, ComplianceResult)
        # Route should be authorized since it's in the allowed list
        assert result.policy_enforced is True
    
    def test_audit_trail_creation(self):
        """Test that audit trail is created for compliance checks"""
        guard = SovereignComplianceGuard()
        
        # Perform a compliance check
        guard.check_compliance("test_operation")
        
        # Check audit trail
        trail = guard.get_audit_trail()
        assert len(trail) > 0
        assert trail[0]["event_type"] == "compliance_check"
        assert trail[0]["operation"] == "test_operation"
        assert "signature" in trail[0]
    
    def test_validate_operation(self):
        """Test quick validation check"""
        guard = SovereignComplianceGuard()
        result = guard.validate_operation("test_operation")
        
        assert isinstance(result, bool)
    
    def test_audit_signature_creation(self):
        """Test cryptographic signature for audit entries"""
        guard = SovereignComplianceGuard()
        
        event_data = {
            "timestamp": datetime.now(UTC).isoformat(),
            "operation": "test",
            "result": "COMPLIANT"
        }
        
        signature = guard._create_audit_signature(event_data)
        assert isinstance(signature, str)
        assert len(signature) == 96  # SHA384 hex digest length
    
    def test_audit_trail_limit(self):
        """Test audit trail retrieval with limit"""
        guard = SovereignComplianceGuard()
        
        # Generate multiple audit entries
        for i in range(10):
            guard.check_compliance(f"operation_{i}")
        
        # Get limited trail
        trail = guard.get_audit_trail(limit=5)
        assert len(trail) <= 5
    
    def test_bridge_resonance_retrieval(self):
        """Test bridge resonance level retrieval"""
        guard = SovereignComplianceGuard()
        resonance = guard._get_bridge_resonance()
        
        assert isinstance(resonance, float)
        assert 0.0 <= resonance <= 1.0
    
    def test_route_policy_check_no_policy_file(self):
        """Test route policy check when policy file doesn't exist"""
        guard = SovereignComplianceGuard()
        
        # Should return True (fail open) when policy file doesn't exist
        result = guard._check_route_policy("/some/random/route")
        assert result is True
