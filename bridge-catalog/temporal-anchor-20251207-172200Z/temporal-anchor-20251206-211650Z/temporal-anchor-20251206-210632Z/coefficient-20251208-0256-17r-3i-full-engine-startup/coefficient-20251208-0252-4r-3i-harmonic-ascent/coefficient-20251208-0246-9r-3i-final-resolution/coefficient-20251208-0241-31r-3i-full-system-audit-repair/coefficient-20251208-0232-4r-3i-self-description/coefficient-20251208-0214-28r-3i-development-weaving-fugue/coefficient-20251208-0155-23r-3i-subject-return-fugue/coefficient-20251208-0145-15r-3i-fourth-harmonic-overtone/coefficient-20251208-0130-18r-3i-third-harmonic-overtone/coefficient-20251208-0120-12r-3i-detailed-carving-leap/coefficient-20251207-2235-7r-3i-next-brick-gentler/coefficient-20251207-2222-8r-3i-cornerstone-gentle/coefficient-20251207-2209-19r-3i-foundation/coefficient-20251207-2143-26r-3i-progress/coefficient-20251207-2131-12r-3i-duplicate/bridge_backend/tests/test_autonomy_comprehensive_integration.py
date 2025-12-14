"""
Comprehensive Autonomy Integration Tests
Tests all autonomy links across engines, tools, runtime, and heritage systems
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch


class TestAutonomyIntegrationSetup:
    """Test autonomy integration initialization"""
    
    @pytest.mark.asyncio
    async def test_genesis_bus_topics_registered(self):
        """Test that all required topics are registered in Genesis bus"""
        from bridge_backend.genesis.bus import genesis_bus
        
        # Super Engines topics
        super_engine_topics = [
            "scrolltongue.analysis", "scrolltongue.translation", "scrolltongue.pattern",
            "commerceforge.trade", "commerceforge.market", "commerceforge.portfolio",
            "auroraforge.visual", "auroraforge.creative", "auroraforge.render",
            "chronicleloom.chronicle", "chronicleloom.timeline", "chronicleloom.event",
            "calculuscore.computation", "calculuscore.optimization", "calculuscore.analysis",
            "qhelmsingularity.quantum", "qhelmsingularity.advanced", "qhelmsingularity.simulation"
        ]
        
        # Specialized engines topics
        specialized_topics = [
            "screen.interaction", "screen.render",
            "indoctrination.training", "indoctrination.knowledge",
            "agents_foundry.agent_created", "agents_foundry.agent_deployed"
        ]
        
        # Core systems topics
        core_topics = [
            "fleet.command", "fleet.status",
            "custody.state", "custody.transfer",
            "console.command", "console.output",
            "captains.policy", "captains.decision",
            "guardians.validation", "guardians.alert",
            "registry.update", "registry.query",
            "doctrine.compliance", "doctrine.violation"
        ]
        
        # Tools and runtime topics
        tools_topics = [
            "firewall.threat", "firewall.analysis",
            "network.diagnostics", "network.status",
            "health.check", "health.status",
            "runtime.deploy", "runtime.status",
            "metrics.snapshot", "metrics.anomaly"
        ]
        
        # Heritage and MAS topics
        heritage_topics = [
            "mas.agent", "mas.coordination", "mas.task", "mas.failure",
            "heritage.agent", "heritage.bridge", "heal.events"
        ]
        
        all_topics = (
            super_engine_topics + specialized_topics + core_topics + 
            tools_topics + heritage_topics
        )
        
        # Check each topic is registered
        for topic in all_topics:
            assert topic in genesis_bus._valid_topics, f"Topic {topic} not registered"
    
    @pytest.mark.asyncio
    async def test_register_all_genesis_links(self):
        """Test that all genesis links can be registered"""
        from bridge_backend.bridge_core.engines.adapters.genesis_link import register_all_genesis_links
        
        # Should not raise an exception
        await register_all_genesis_links()


class TestSuperEnginesAutonomyLinks:
    """Test Six Super Engines autonomy integration"""
    
    @pytest.mark.asyncio
    async def test_super_engines_autonomy_registration(self):
        """Test super engines autonomy links registration"""
        from bridge_backend.bridge_core.engines.adapters.super_engines_autonomy_link import (
            register_super_engines_autonomy_links
        )
        
        await register_super_engines_autonomy_links()
    
    @pytest.mark.asyncio
    async def test_super_engines_autonomy_validation(self):
        """Test super engines autonomy integration validation"""
        from bridge_backend.bridge_core.engines.adapters.super_engines_autonomy_link import (
            validate_super_engines_autonomy_integration
        )
        
        result = await validate_super_engines_autonomy_integration()
        
        # Should have all required topics
        assert "success" in result
        assert "total_topics" in result
        assert result["total_topics"] == 18  # 6 engines × 3 topics each
    
    @pytest.mark.asyncio
    async def test_scrolltongue_event_handling(self):
        """Test ScrollTongue events are forwarded to autonomy"""
        from bridge_backend.genesis.bus import genesis_bus
        
        received_events = []
        
        async def capture_event(event):
            received_events.append(event)
        
        # Subscribe to autonomy intent
        genesis_bus.subscribe("genesis.intent", capture_event)
        
        # Publish a ScrollTongue event
        await genesis_bus.publish("scrolltongue.analysis", {
            "type": "language_analysis",
            "text": "test",
            "language": "en"
        })
        
        # Allow event processing
        await asyncio.sleep(0.1)
        
        # Should have received autonomy event
        autonomy_events = [e for e in received_events if e.get("type") == "autonomy.scrolltongue_analysis"]
        assert len(autonomy_events) > 0


class TestCoreSystemsAutonomyLinks:
    """Test core systems autonomy integration"""
    
    @pytest.mark.asyncio
    async def test_guardians_safety_validation(self):
        """Test that Guardians block dangerous autonomy actions"""
        from bridge_backend.genesis.bus import genesis_bus
        
        received_events = []
        
        async def capture_event(event):
            received_events.append(event)
        
        # Subscribe to genesis.heal
        genesis_bus.subscribe("genesis.heal", capture_event)
        
        # Publish a dangerous guardians event
        await genesis_bus.publish("guardians.validation", {
            "type": "recursive_action",
            "action": "recursive delete all"
        })
        
        # Allow event processing
        await asyncio.sleep(0.1)
        
        # Should have received blocked action event
        blocked_events = [e for e in received_events if e.get("type") == "autonomy.action_blocked"]
        assert len(blocked_events) > 0
    
    @pytest.mark.asyncio
    async def test_doctrine_violation_triggers_healing(self):
        """Test that doctrine violations trigger autonomy healing"""
        from bridge_backend.genesis.bus import genesis_bus
        
        received_events = []
        
        async def capture_event(event):
            received_events.append(event)
        
        # Subscribe to genesis.heal
        genesis_bus.subscribe("genesis.heal", capture_event)
        
        # Publish a doctrine violation
        await genesis_bus.publish("doctrine.violation", {
            "type": "violation",
            "rule": "test_rule",
            "severity": "high"
        })
        
        # Allow event processing
        await asyncio.sleep(0.1)
        
        # Should have received healing event
        healing_events = [e for e in received_events if e.get("type") == "autonomy.doctrine_violation"]
        assert len(healing_events) > 0


class TestToolsRuntimeAutonomyLinks:
    """Test tools and runtime autonomy integration"""
    
    @pytest.mark.asyncio
    async def test_health_degraded_triggers_healing(self):
        """Test that degraded health status triggers autonomy healing"""
        from bridge_backend.genesis.bus import genesis_bus
        
        received_events = []
        
        async def capture_event(event):
            received_events.append(event)
        
        # Subscribe to genesis.heal
        genesis_bus.subscribe("genesis.heal", capture_event)
        
        # Publish a health degradation event
        await genesis_bus.publish("health.status", {
            "component": "test_component",
            "status": "degraded",
            "details": {"error": "test error"}
        })
        
        # Allow event processing
        await asyncio.sleep(0.1)
        
        # Should have received healing event
        healing_events = [e for e in received_events if e.get("type") == "autonomy.health_degraded"]
        assert len(healing_events) > 0
    
    @pytest.mark.asyncio
    async def test_firewall_threat_triggers_healing(self):
        """Test that high firewall threats trigger autonomy healing"""
        from bridge_backend.genesis.bus import genesis_bus
        
        received_events = []
        
        async def capture_event(event):
            received_events.append(event)
        
        # Subscribe to genesis.heal
        genesis_bus.subscribe("genesis.heal", capture_event)
        
        # Publish a high-threat firewall event
        await genesis_bus.publish("firewall.threat", {
            "threat_level": 8,
            "source_ip": "192.0.2.1",
            "attack_type": "sql_injection"
        })
        
        # Allow event processing
        await asyncio.sleep(0.1)
        
        # Should have received healing event
        healing_events = [e for e in received_events if e.get("type") == "autonomy.firewall_threat"]
        assert len(healing_events) > 0
    
    @pytest.mark.asyncio
    async def test_network_error_triggers_healing(self):
        """Test that network errors trigger autonomy healing"""
        from bridge_backend.genesis.bus import genesis_bus
        
        received_events = []
        
        async def capture_event(event):
            received_events.append(event)
        
        # Subscribe to genesis.heal
        genesis_bus.subscribe("genesis.heal", capture_event)
        
        # Publish a network error event
        await genesis_bus.publish("network.status", {
            "status": "error",
            "error": "connection_timeout",
            "latency": 5000
        })
        
        # Allow event processing
        await asyncio.sleep(0.1)
        
        # Should have received healing event
        healing_events = [e for e in received_events if e.get("type") == "autonomy.network_issue"]
        assert len(healing_events) > 0


class TestHeritageMASAutonomyLinks:
    """Test Heritage and MAS autonomy integration"""
    
    @pytest.mark.asyncio
    async def test_mas_agent_failure_triggers_healing(self):
        """Test that MAS agent failures trigger autonomy healing"""
        from bridge_backend.genesis.bus import genesis_bus
        
        received_events = []
        
        async def capture_event(event):
            received_events.append(event)
        
        # Subscribe to genesis.heal
        genesis_bus.subscribe("genesis.heal", capture_event)
        
        # Publish a MAS failure event
        await genesis_bus.publish("mas.failure", {
            "kind": "agent_failure",
            "agent_id": "test_agent",
            "error": "timeout"
        })
        
        # Allow event processing
        await asyncio.sleep(0.1)
        
        # Should have received healing event
        healing_events = [e for e in received_events if e.get("type") == "autonomy.mas_agent_failure"]
        assert len(healing_events) > 0
    
    @pytest.mark.asyncio
    async def test_mas_coordination_publishes_intent(self):
        """Test that MAS coordination events publish to genesis.intent"""
        from bridge_backend.genesis.bus import genesis_bus
        
        received_events = []
        
        async def capture_event(event):
            received_events.append(event)
        
        # Subscribe to genesis.intent
        genesis_bus.subscribe("genesis.intent", capture_event)
        
        # Publish a MAS coordination event
        await genesis_bus.publish("mas.coordination", {
            "kind": "task_coordination",
            "agents": ["agent1", "agent2"],
            "task": "test_task"
        })
        
        # Allow event processing
        await asyncio.sleep(0.1)
        
        # Should have received intent event
        intent_events = [e for e in received_events if e.get("type") == "autonomy.mas_coordination"]
        assert len(intent_events) > 0


class TestAutonomyUtilityFunctions:
    """Test autonomy integration utility functions"""
    
    @pytest.mark.asyncio
    async def test_publish_health_event(self):
        """Test health event publishing utility"""
        from bridge_backend.bridge_core.engines.adapters.tools_runtime_autonomy_link import (
            publish_health_event
        )
        from bridge_backend.genesis.bus import genesis_bus
        
        received_events = []
        
        async def capture_event(event):
            received_events.append(event)
        
        genesis_bus.subscribe("health.status", capture_event)
        
        await publish_health_event("test_component", "healthy", {"detail": "test"})
        
        await asyncio.sleep(0.1)
        
        assert len(received_events) > 0
        assert received_events[0]["component"] == "test_component"
    
    @pytest.mark.asyncio
    async def test_publish_mas_event(self):
        """Test MAS event publishing utility"""
        from bridge_backend.bridge_core.engines.adapters.heritage_mas_autonomy_link import (
            publish_mas_event
        )
        from bridge_backend.genesis.bus import genesis_bus
        
        received_events = []
        
        async def capture_event(event):
            received_events.append(event)
        
        genesis_bus.subscribe("mas.agent", capture_event)
        
        await publish_mas_event("agent", {"agent_id": "test", "status": "active"})
        
        await asyncio.sleep(0.1)
        
        assert len(received_events) > 0
        assert received_events[0]["agent_id"] == "test"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
