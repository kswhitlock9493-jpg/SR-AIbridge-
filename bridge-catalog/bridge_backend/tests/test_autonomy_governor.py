"""
Test Autonomy Governor
"""

import pytest
from datetime import datetime, timezone, timedelta
from bridge_backend.engines.autonomy.governor import AutonomyGovernor
from bridge_backend.engines.autonomy.models import Incident, Decision


class TestAutonomyGovernor:
    """Test the Autonomy Governor decision-making and execution"""
    
    def test_governor_initialization(self):
        """Test governor initializes with correct defaults"""
        gov = AutonomyGovernor()
        assert gov.max_actions_per_hour == 6
        assert gov.cooldown.total_seconds() == 5 * 60  # 5 minutes
        assert gov.fail_streak_trip == 3
        assert gov.fail_streak == 0
        assert len(gov.window) == 0
    
    @pytest.mark.asyncio
    async def test_decide_netlify_preview_failed(self):
        """Test decision for Netlify preview failure"""
        gov = AutonomyGovernor()
        incident = Incident(
            kind="deploy.netlify.preview_failed",
            source="github"
        )
        
        decision = await gov.decide(incident)
        assert decision.action == "REPAIR_CONFIG"
        assert decision.targets == ["netlify"]
        assert decision.reason == "preview_failed"
    
    @pytest.mark.asyncio
    async def test_decide_render_deploy_failed(self):
        """Test decision for Render deployment failure"""
        gov = AutonomyGovernor()
        incident = Incident(
            kind="deploy.render.failed",
            source="render"
        )
        
        decision = await gov.decide(incident)
        assert decision.action == "RETRY"
        assert decision.reason == "render_retry_once"
    
    @pytest.mark.asyncio
    async def test_decide_env_drift(self):
        """Test decision for environment drift"""
        gov = AutonomyGovernor()
        incident = Incident(
            kind="envrecon.drift",
            source="envrecon"
        )
        
        decision = await gov.decide(incident)
        assert decision.action == "SYNC_ENVS"
        assert decision.reason == "envrecon_drift"
    
    @pytest.mark.asyncio
    async def test_decide_code_integrity(self):
        """Test decision for code integrity issues"""
        gov = AutonomyGovernor()
        incident = Incident(
            kind="arie.deprecated.detected",
            source="arie"
        )
        
        decision = await gov.decide(incident)
        assert decision.action == "REPAIR_CODE"
        assert decision.reason == "arie_safe_edit"
    
    @pytest.mark.asyncio
    async def test_decide_unknown_incident(self):
        """Test decision for unknown incident kind"""
        gov = AutonomyGovernor()
        incident = Incident(
            kind="unknown.incident.type",
            source="test"
        )
        
        decision = await gov.decide(incident)
        assert decision.action == "NOOP"
        assert decision.reason == "unrecognized_incident"
    
    @pytest.mark.asyncio
    async def test_rate_limiting(self):
        """Test that governor enforces rate limiting"""
        now = datetime.now(timezone.utc)
        gov = AutonomyGovernor(now=now)
        
        # Fill the window with 6 actions in the last hour
        for i in range(6):
            gov.window.append(now - timedelta(minutes=i))
        
        incident = Incident(
            kind="deploy.netlify.preview_failed",
            source="test"
        )
        
        decision = await gov.decide(incident)
        assert decision.action == "NOOP"
        assert decision.reason == "rate_limited"
    
    @pytest.mark.asyncio
    async def test_cooldown(self):
        """Test that governor enforces cooldown between actions"""
        now = datetime.now(timezone.utc)
        gov = AutonomyGovernor(now=now)
        
        # Set last action to 2 minutes ago (within 5-minute cooldown)
        gov.last_action_at = now - timedelta(minutes=2)
        
        incident = Incident(
            kind="deploy.netlify.preview_failed",
            source="test"
        )
        
        decision = await gov.decide(incident)
        assert decision.action == "NOOP"
        assert decision.reason == "cooldown"
    
    @pytest.mark.asyncio
    async def test_circuit_breaker(self):
        """Test that circuit breaker trips after consecutive failures"""
        gov = AutonomyGovernor()
        
        # Simulate 3 consecutive failures
        gov.fail_streak = 3
        
        incident = Incident(
            kind="deploy.netlify.preview_failed",
            source="test"
        )
        
        decision = await gov.decide(incident)
        assert decision.action == "ESCALATE"
        assert decision.reason == "circuit_breaker_tripped"
    
    @pytest.mark.asyncio
    async def test_rate_limit_window_cleanup(self):
        """Test that old actions are removed from rate limit window"""
        now = datetime.now(timezone.utc)
        gov = AutonomyGovernor(now=now)
        
        # Add 3 old actions (>1 hour ago) and 2 recent ones
        gov.window = [
            now - timedelta(hours=2),
            now - timedelta(hours=1, minutes=5),
            now - timedelta(hours=1, minutes=1),
            now - timedelta(minutes=30),
            now - timedelta(minutes=10),
        ]
        
        incident = Incident(
            kind="deploy.netlify.preview_failed",
            source="test"
        )
        
        decision = await gov.decide(incident)
        
        # Should have cleaned up old actions (only 2 remain in window)
        assert len(gov.window) == 2
        assert decision.action == "REPAIR_CONFIG"  # Not rate limited
