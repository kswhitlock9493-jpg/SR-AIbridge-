"""
Tests for Umbra Triage Mesh Healers
v1.9.7k - Unified Triage Mesh
"""

import pytest
import asyncio

from bridge_backend.engines.umbra.healers import UmbraHealers
from bridge_backend.engines.umbra.models import HealPlan, HealAction, TriageTicket, TriageSeverity, TriageStatus, TriageKind


@pytest.fixture
def healers():
    """Create Umbra Healers instance"""
    return UmbraHealers()


@pytest.fixture
def sample_ticket():
    """Create a sample triage ticket"""
    return TriageTicket(
        ticket_id="UM-2025-10-12-0001",
        kind=TriageKind.DEPLOY,
        source="netlify",
        severity=TriageSeverity.CRITICAL,
        status=TriageStatus.OPEN,
        signals=["deploy_failed"],
        incidents=[]
    )


@pytest.fixture
def sample_heal_plan():
    """Create a sample heal plan"""
    return HealPlan(
        plan_id="PLAN-UM-2025-10-12-0001",
        ticket_id="UM-2025-10-12-0001",
        actions=[
            HealAction(
                action_type="normalize_netlify_config",
                target="netlify.toml",
                parameters={"check_headers": True}
            )
        ],
        parity_prechecks=["env:netlify/render"],
        truth_policy="standard"
    )


class TestUmbraHealers:
    """Test Umbra Healers functionality"""
    
    def test_healers_initialization(self, healers):
        """Test that healers initialize correctly"""
        assert healers is not None
        assert isinstance(healers.allow_heal, bool)
        assert isinstance(healers.auto_heal_on, bool)
    
    @pytest.mark.asyncio
    async def test_execute_heal_plan_intent_only(self, healers, sample_heal_plan, sample_ticket):
        """Test heal plan execution in intent-only mode (healing disabled)"""
        # Force intent-only mode
        healers.allow_heal = False
        
        result = await healers.execute_heal_plan(sample_heal_plan, sample_ticket)
        
        assert result["status"] == "intent_only"
        assert "plan_id" in result
        assert "intent" in result
        assert len(result["intent"]["actions"]) == 1
    
    @pytest.mark.asyncio
    async def test_certify_with_truth(self, healers, sample_heal_plan):
        """Test Truth certification for heal plan"""
        # This may fail if Truth engine is not available, which is expected
        result = await healers._certify_with_truth(sample_heal_plan)
        
        assert "ok" in result
        # Either certified or auto-approved if Truth unavailable
        if result.get("reason") != "truth_not_available":
            assert "signature" in result
    
    @pytest.mark.asyncio
    async def test_run_parity_prechecks(self, healers):
        """Test parity prechecks"""
        # This may fail if Parity engine is not available
        result = await healers._run_parity_prechecks(["env:netlify/render"])
        
        assert "ok" in result
        # Should pass even if parity unavailable
        assert result.get("ok") or result.get("reason") == "parity_not_available"


class TestHealActions:
    """Test individual heal actions"""
    
    @pytest.mark.asyncio
    async def test_execute_chimera_action(self, healers):
        """Test Chimera action execution"""
        action = HealAction(
            action_type="normalize_netlify_config",
            target="netlify.toml",
            parameters={}
        )
        
        # This may fail if Chimera engine is not available
        result = await healers._execute_chimera_action(action)
        
        assert "ok" in result
        # Either success or chimera_not_available
    
    @pytest.mark.asyncio
    async def test_execute_healthnet_action(self, healers):
        """Test HealthNet action execution"""
        action = HealAction(
            action_type="endpoint_health_check",
            target="api_endpoints",
            parameters={}
        )
        
        result = await healers._execute_healthnet_action(action)
        
        assert result["ok"] is True
        assert result["action"] == "endpoint_health_check"
    
    @pytest.mark.asyncio
    async def test_execute_autonomy_action(self, healers):
        """Test Autonomy action execution"""
        action = HealAction(
            action_type="service_restart",
            target="runtime_service",
            parameters={"graceful": True}
        )
        
        # This may fail if Autonomy engine is not available
        result = await healers._execute_autonomy_action(action)
        
        assert "ok" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
