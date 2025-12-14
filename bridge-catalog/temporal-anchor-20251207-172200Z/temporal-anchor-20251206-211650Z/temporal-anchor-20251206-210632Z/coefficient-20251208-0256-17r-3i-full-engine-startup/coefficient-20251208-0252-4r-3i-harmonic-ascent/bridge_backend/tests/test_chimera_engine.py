"""
Tests for Chimera Deployment Engine
"""

import pytest
import asyncio
from pathlib import Path
from bridge_backend.bridge_core.engines.chimera import (
    ChimeraDeploymentEngine,
    ChimeraConfig,
    get_chimera_instance
)


class TestChimeraConfig:
    """Test ChimeraConfig dataclass"""
    
    def test_config_defaults(self):
        """Test default configuration values"""
        config = ChimeraConfig()
        
        assert config.engine == "CHIMERA_DEPLOYMENT_ENGINE"
        assert config.codename == "HXO-Echelon-03"
        assert config.core_protocol == "Predictive_Autonomous_Deployment"
        assert config.autonomy_level == "TOTAL"
        assert config.simulate_before_deploy is True
        assert config.heal_on_detected_drift is True
        assert config.truth_signoff_required is True
    
    def test_config_to_dict(self):
        """Test configuration export to dict"""
        config = ChimeraConfig()
        config_dict = config.to_dict()
        
        assert "engine" in config_dict
        assert "codename" in config_dict
        assert "policies" in config_dict
        assert config_dict["policies"]["simulate_before_deploy"] is True
    
    def test_config_to_json(self):
        """Test configuration export to JSON"""
        config = ChimeraConfig()
        json_str = config.to_json()
        
        assert isinstance(json_str, str)
        assert "CHIMERA_DEPLOYMENT_ENGINE" in json_str
        assert "HXO-Echelon-03" in json_str


class TestChimeraEngine:
    """Test ChimeraDeploymentEngine core functionality"""
    
    def test_engine_initialization(self):
        """Test engine initialization"""
        config = ChimeraConfig()
        engine = ChimeraDeploymentEngine(config)
        
        assert engine.config is not None
        assert engine.simulator is not None
        assert engine.healer is not None
        assert engine.certifier is not None
        assert engine.enabled is True
    
    def test_singleton_instance(self):
        """Test get_chimera_instance returns singleton"""
        instance1 = get_chimera_instance()
        instance2 = get_chimera_instance()
        
        assert instance1 is instance2
    
    @pytest.mark.asyncio
    async def test_simulate_netlify(self):
        """Test Netlify simulation"""
        config = ChimeraConfig()
        engine = ChimeraDeploymentEngine(config)
        
        # Use current directory for test
        project_path = Path.cwd()
        result = await engine.simulate("netlify", project_path)
        
        assert "status" in result
        assert "timestamp" in result
        assert "issues" in result
        assert "warnings" in result
        assert "duration_seconds" in result
    
    @pytest.mark.asyncio
    async def test_simulate_render(self):
        """Test Render simulation"""
        config = ChimeraConfig()
        engine = ChimeraDeploymentEngine(config)
        
        project_path = Path.cwd()
        result = await engine.simulate("render", project_path)
        
        assert "status" in result
        assert "timestamp" in result
        assert "issues" in result
        assert "warnings" in result
    
    @pytest.mark.asyncio
    async def test_monitor(self):
        """Test engine monitoring"""
        config = ChimeraConfig()
        engine = ChimeraDeploymentEngine(config)
        
        status = await engine.monitor()
        
        assert "enabled" in status
        assert "config" in status
        assert "deployments_count" in status
        assert "timestamp" in status
        assert status["enabled"] is True


class TestChimeraSimulator:
    """Test BuildSimulator component"""
    
    @pytest.mark.asyncio
    async def test_simulator_initialization(self):
        """Test simulator initialization"""
        from bridge_backend.bridge_core.engines.chimera.simulator import BuildSimulator
        
        config = ChimeraConfig()
        simulator = BuildSimulator(config)
        
        assert simulator.config is not None
        assert simulator.simulation_timeout == 300
    
    @pytest.mark.asyncio
    async def test_netlify_simulation_structure(self):
        """Test Netlify simulation result structure"""
        from bridge_backend.bridge_core.engines.chimera.simulator import BuildSimulator
        
        config = ChimeraConfig()
        simulator = BuildSimulator(config)
        
        result = await simulator.simulate_netlify_build(Path.cwd())
        
        assert "status" in result
        assert "issues" in result
        assert "warnings" in result
        assert "issues_count" in result
        assert "warnings_count" in result
        assert "simulation_accuracy" in result
        assert result["simulation_accuracy"] == "99.8%"


class TestChimeraHealer:
    """Test ConfigurationHealer component"""
    
    @pytest.mark.asyncio
    async def test_healer_initialization(self):
        """Test healer initialization"""
        from bridge_backend.bridge_core.engines.chimera.healer import ConfigurationHealer
        
        config = ChimeraConfig()
        healer = ConfigurationHealer(config)
        
        assert healer.config is not None
        assert healer.max_attempts == 3
    
    @pytest.mark.asyncio
    async def test_healing_result_structure(self):
        """Test healing result structure"""
        from bridge_backend.bridge_core.engines.chimera.healer import ConfigurationHealer
        
        config = ChimeraConfig()
        healer = ConfigurationHealer(config)
        
        # Test with empty issues list
        result = await healer.heal_netlify_config([], Path.cwd())
        
        assert "status" in result
        assert "platform" in result
        assert "fixes_applied" in result
        assert "fixes_failed" in result
        assert result["platform"] == "netlify"


class TestChimeraCertifier:
    """Test DeploymentCertifier component"""
    
    @pytest.mark.asyncio
    async def test_certifier_initialization(self):
        """Test certifier initialization"""
        from bridge_backend.bridge_core.engines.chimera.certifier import DeploymentCertifier
        
        config = ChimeraConfig()
        certifier = DeploymentCertifier(config)
        
        assert certifier.config is not None
        assert certifier.certifications == []
    
    @pytest.mark.asyncio
    async def test_certification_structure(self):
        """Test certification result structure"""
        from bridge_backend.bridge_core.engines.chimera.certifier import DeploymentCertifier
        
        config = ChimeraConfig()
        certifier = DeploymentCertifier(config)
        
        # Create mock simulation result (success case)
        simulation_result = {
            "status": "passed",
            "timestamp": "2025-10-12T00:00:00",
            "issues": [],
            "issues_count": 0
        }
        
        certification = await certifier.certify_build(simulation_result)
        
        assert "certified" in certification
        assert "timestamp" in certification
        assert "protocol" in certification
        assert "checks" in certification
        assert "signature" in certification
        assert "verification_chain" in certification
        assert certification["protocol"] == "TRUTH_CERT_V3"
    
    @pytest.mark.asyncio
    async def test_certification_passes_with_no_issues(self):
        """Test that certification passes with clean simulation"""
        from bridge_backend.bridge_core.engines.chimera.certifier import DeploymentCertifier
        
        config = ChimeraConfig()
        certifier = DeploymentCertifier(config)
        
        simulation_result = {
            "status": "passed",
            "timestamp": "2025-10-12T00:00:00",
            "issues": [],
            "issues_count": 0
        }
        
        certification = await certifier.certify_build(simulation_result)
        
        assert certification["certified"] is True
        assert all(certification["checks"].values())
    
    @pytest.mark.asyncio
    async def test_certification_fails_with_critical_issues(self):
        """Test that certification fails with critical issues"""
        from bridge_backend.bridge_core.engines.chimera.certifier import DeploymentCertifier
        
        config = ChimeraConfig()
        certifier = DeploymentCertifier(config)
        
        simulation_result = {
            "status": "failed",
            "timestamp": "2025-10-12T00:00:00",
            "issues": [
                {
                    "type": "critical_error",
                    "severity": "critical",
                    "message": "Build failed"
                }
            ],
            "issues_count": 1
        }
        
        certification = await certifier.certify_build(simulation_result)
        
        assert certification["certified"] is False
        assert certification["checks"]["no_critical_issues"] is False


class TestChimeraIntegration:
    """Integration tests for full Chimera pipeline"""
    
    @pytest.mark.asyncio
    async def test_full_deployment_flow_structure(self):
        """Test that full deployment flow returns expected structure"""
        config = ChimeraConfig()
        engine = ChimeraDeploymentEngine(config)
        
        # Run deployment (will be dry-run mode)
        result = await engine.deploy(
            platform="netlify",
            project_path=Path.cwd(),
            auto_heal=False,
            certify=True
        )
        
        assert "status" in result
        assert "platform" in result
        assert "timestamp" in result
        assert "simulation" in result or "error" in result
        
        # If simulation ran, check its structure
        if "simulation" in result:
            assert "status" in result["simulation"]
            assert "issues" in result["simulation"]


class TestGenesisIntegration:
    """Test Genesis Bus integration"""
    
    def test_genesis_topics_registered(self):
        """Test that Chimera topics are registered in Genesis Bus"""
        from bridge_backend.genesis.bus import GenesisEventBus
        
        bus = GenesisEventBus()
        
        # Check Chimera topics are in valid topics
        chimera_topics = [
            "deploy.initiated",
            "deploy.heal.intent",
            "deploy.heal.complete",
            "deploy.certified",
            "chimera.simulate.start",
            "chimera.simulate.complete",
            "chimera.deploy.start",
            "chimera.deploy.complete",
            "chimera.rollback.triggered"
        ]
        
        for topic in chimera_topics:
            assert topic in bus._valid_topics, f"Topic {topic} not registered"


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
