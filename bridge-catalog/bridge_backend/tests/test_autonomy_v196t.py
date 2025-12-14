"""
Test Autonomy Governor v1.9.6t Features
"""

import pytest
from datetime import datetime, timezone, timedelta
from bridge_backend.engines.autonomy.governor import AutonomyGovernor
from bridge_backend.engines.autonomy.models import Incident, Decision


class TestAutonomyGovernorV196T:
    """Test the v1.9.6t enhancements to Autonomy Governor"""
    
    def test_reinforcement_scoring_initialization(self):
        """Test that engine success rates are initialized"""
        gov = AutonomyGovernor()
        assert "ARIE" in gov.engine_success_rates
        assert "Chimera" in gov.engine_success_rates
        assert "EnvRecon" in gov.engine_success_rates
        assert "Truth" in gov.engine_success_rates
        assert 0.0 <= gov.engine_success_rates["ARIE"] <= 1.0
    
    def test_calculate_reinforcement_score(self):
        """Test reinforcement score calculation"""
        gov = AutonomyGovernor()
        
        # Base score without cooldown
        score = gov._calculate_reinforcement_score("REPAIR_CODE", "ARIE")
        assert 0.0 <= score <= 1.0
        assert score == gov.engine_success_rates["ARIE"]
        
        # Score with cooldown penalty
        gov.last_action_at = gov.now - timedelta(minutes=2)
        score_with_penalty = gov._calculate_reinforcement_score("REPAIR_CODE", "ARIE")
        assert score_with_penalty < score
    
    @pytest.mark.asyncio
    async def test_decide_create_secret(self):
        """Test decision for GitHub secret missing"""
        gov = AutonomyGovernor()
        incident = Incident(
            kind="github.secret.missing",
            source="github",
            details={"secrets": ["API_KEY", "TOKEN"]}
        )
        
        decision = await gov.decide(incident)
        assert decision.action == "CREATE_SECRET"
        assert decision.reason == "github_sync"
        assert decision.targets == ["API_KEY", "TOKEN"]
    
    @pytest.mark.asyncio
    async def test_decide_regenerate_config(self):
        """Test decision for config outdated"""
        gov = AutonomyGovernor()
        incident = Incident(
            kind="config.outdated",
            source="system",
            details={"platforms": ["netlify", "render"]}
        )
        
        decision = await gov.decide(incident)
        assert decision.action == "REGENERATE_CONFIG"
        assert decision.reason == "config_refresh"
        assert decision.targets == ["netlify", "render"]
    
    @pytest.mark.asyncio
    async def test_decide_sync_and_certify(self):
        """Test decision for deploy failure requiring sync and certify"""
        gov = AutonomyGovernor()
        incident = Incident(
            kind="deploy.failure",
            source="github",
            details={"workflow": "build-deploy"}
        )
        
        decision = await gov.decide(incident)
        assert decision.action == "SYNC_AND_CERTIFY"
        assert decision.reason == "deploy_heal"
    
    @pytest.mark.asyncio
    async def test_engine_success_rate_update(self):
        """Test that engine success rates are updated after execution"""
        gov = AutonomyGovernor()
        
        initial_rate = gov.engine_success_rates["ARIE"]
        
        # Update with success
        await gov._update_engine_success_rate("REPAIR_CODE", True)
        success_rate = gov.engine_success_rates["ARIE"]
        assert success_rate > initial_rate or success_rate == 1.0
        
        # Reset
        gov.engine_success_rates["ARIE"] = 0.5
        
        # Update with failure
        await gov._update_engine_success_rate("REPAIR_CODE", False)
        failure_rate = gov.engine_success_rates["ARIE"]
        assert failure_rate < 0.5
    
    @pytest.mark.asyncio
    async def test_generate_certificate(self):
        """Test certificate generation"""
        gov = AutonomyGovernor()
        
        decision = Decision(
            action="REPAIR_CONFIG",
            reason="test",
            targets=["netlify"]
        )
        
        report = {"status": "success", "platform": "netlify"}
        certified = {"ok": True, "result": {"certified": True}}
        
        cert = await gov._generate_certificate(decision, report, certified)
        
        assert "timestamp" in cert
        assert "action" in cert
        assert cert["action"] == "REPAIR_CONFIG"
        assert "certificate_hash" in cert
        assert "report_hash" in cert
        assert len(cert["certificate_hash"]) == 64  # SHA256 hex length
    
    @pytest.mark.asyncio
    async def test_predict_success(self):
        """Test success prediction integration"""
        gov = AutonomyGovernor()
        
        decision = Decision(
            action="REPAIR_CONFIG",
            reason="test",
            targets=["netlify"]
        )
        
        report = {"status": "success"}
        
        prediction = await gov._predict_success(decision, report)
        
        # Should return either None (if Leviathan not available) or a float
        assert prediction is None or (0.0 <= prediction <= 1.0)
    
    @pytest.mark.asyncio
    async def test_update_blueprint_policy(self):
        """Test Blueprint policy update integration"""
        gov = AutonomyGovernor()
        
        decision = Decision(
            action="REPAIR_CONFIG",
            reason="test",
            targets=["netlify"]
        )
        
        # Should not raise an error
        await gov._update_blueprint_policy(decision, True)
        await gov._update_blueprint_policy(decision, False)
