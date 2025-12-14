"""
Test Suite for v2.0.0 Genesis Framework
Validates universal engine integration
"""

import pytest
import asyncio
from typing import Dict, Any


class TestGenesisEventBus:
    """Test Genesis event bus multiplexer"""
    
    @pytest.mark.asyncio
    async def test_bus_initialization(self):
        """Test Genesis bus initializes correctly"""
        from bridge_backend.genesis.bus import GenesisEventBus
        
        bus = GenesisEventBus()
        assert bus.is_enabled() is True
        stats = bus.get_stats()
        assert stats["enabled"] is True
        assert stats["total_events"] == 0
    
    @pytest.mark.asyncio
    async def test_event_publish_subscribe(self):
        """Test event publishing and subscription"""
        from bridge_backend.genesis.bus import GenesisEventBus
        
        bus = GenesisEventBus()
        received_events = []
        
        def handler(event: Dict[str, Any]):
            received_events.append(event)
        
        bus.subscribe("genesis.intent", handler)
        
        await bus.publish("genesis.intent", {
            "type": "test.event",
            "data": "test_data"
        })
        
        assert len(received_events) == 1
        assert received_events[0]["type"] == "test.event"
        assert received_events[0]["data"] == "test_data"
        assert "_genesis_timestamp" in received_events[0]
        assert "_genesis_seq" in received_events[0]
    
    @pytest.mark.asyncio
    async def test_event_history(self):
        """Test event history tracking"""
        from bridge_backend.genesis.bus import GenesisEventBus
        
        bus = GenesisEventBus()
        
        await bus.publish("genesis.fact", {"type": "test.fact"})
        await bus.publish("genesis.heal", {"type": "test.heal"})
        
        history = bus.get_event_history()
        assert len(history) >= 2
        assert history[-2]["topic"] == "genesis.fact"
        assert history[-1]["topic"] == "genesis.heal"
    
    @pytest.mark.asyncio
    async def test_multiple_subscribers(self):
        """Test multiple subscribers to same topic"""
        from bridge_backend.genesis.bus import GenesisEventBus
        
        bus = GenesisEventBus()
        handler1_calls = []
        handler2_calls = []
        
        def handler1(event: Dict[str, Any]):
            handler1_calls.append(event)
        
        def handler2(event: Dict[str, Any]):
            handler2_calls.append(event)
        
        bus.subscribe("genesis.echo", handler1)
        bus.subscribe("genesis.echo", handler2)
        
        await bus.publish("genesis.echo", {"type": "test.echo"})
        
        assert len(handler1_calls) == 1
        assert len(handler2_calls) == 1


class TestGenesisManifest:
    """Test Genesis manifest system"""
    
    def test_manifest_initialization(self):
        """Test manifest initializes correctly"""
        from bridge_backend.genesis.manifest import GenesisManifest
        
        manifest = GenesisManifest()
        assert manifest.list_engines() == []
    
    def test_engine_registration(self):
        """Test engine registration"""
        from bridge_backend.genesis.manifest import GenesisManifest
        
        manifest = GenesisManifest()
        
        schema = {
            "name": "test_engine",
            "description": "Test engine",
            "genesis_role": "Test component",
            "topics": ["test.topic"],
            "dependencies": [],
        }
        
        manifest.register_engine("test_engine", schema)
        
        assert "test_engine" in manifest.list_engines()
        engine = manifest.get_engine("test_engine")
        assert engine is not None
        assert engine["genesis_role"] == "Test component"
    
    def test_engine_dependencies(self):
        """Test engine dependency tracking"""
        from bridge_backend.genesis.manifest import GenesisManifest
        
        manifest = GenesisManifest()
        
        # Register base engine
        manifest.register_engine("base", {
            "genesis_role": "Base",
            "dependencies": [],
        })
        
        # Register dependent engine
        manifest.register_engine("dependent", {
            "genesis_role": "Dependent",
            "dependencies": ["base"],
        })
        
        deps = manifest.get_dependencies("dependent")
        assert "base" in deps
    
    def test_manifest_validation(self):
        """Test manifest integrity validation"""
        from bridge_backend.genesis.manifest import GenesisManifest
        
        manifest = GenesisManifest()
        
        manifest.register_engine("engine1", {
            "genesis_role": "Engine 1",
            "dependencies": [],
        })
        
        manifest.register_engine("engine2", {
            "genesis_role": "Engine 2",
            "dependencies": ["engine1"],
        })
        
        validation = manifest.validate_integrity()
        assert validation["valid"] is True
        assert validation["engine_count"] == 2
    
    def test_missing_dependency_detection(self):
        """Test detection of missing dependencies"""
        from bridge_backend.genesis.manifest import GenesisManifest
        
        manifest = GenesisManifest()
        
        manifest.register_engine("engine1", {
            "genesis_role": "Engine 1",
            "dependencies": ["missing_engine"],
        })
        
        validation = manifest.validate_integrity()
        assert validation["valid"] is False
        assert len(validation["errors"]) > 0
    
    def test_blueprint_sync(self):
        """Test syncing from Blueprint Registry"""
        from bridge_backend.genesis.manifest import GenesisManifest
        
        manifest = GenesisManifest()
        
        # This should not raise an error even if Blueprint Registry is unavailable
        manifest.sync_from_blueprint_registry()
        
        # If Blueprint Registry is available, engines should be registered
        engines = manifest.list_engines()
        # We don't assert specific count as it depends on Blueprint availability


class TestGenesisIntrospection:
    """Test Genesis introspection system"""
    
    def test_introspection_initialization(self):
        """Test introspection initializes correctly"""
        from bridge_backend.genesis.introspection import GenesisIntrospection
        
        introspection = GenesisIntrospection()
        health = introspection.get_health_status()
        assert health["overall_healthy"] is True
        assert health["total_count"] == 0
    
    def test_metric_recording(self):
        """Test metric recording and retrieval"""
        from bridge_backend.genesis.introspection import GenesisIntrospection
        
        introspection = GenesisIntrospection()
        
        introspection.record_metric("test_metric", 42, {"unit": "requests"})
        
        metric = introspection.get_metric("test_metric")
        assert metric is not None
        assert metric["value"] == 42
        assert metric["metadata"]["unit"] == "requests"
    
    def test_health_updates(self):
        """Test health status updates"""
        from bridge_backend.genesis.introspection import GenesisIntrospection
        
        introspection = GenesisIntrospection()
        
        introspection.update_health("engine1", True)
        introspection.update_health("engine2", False)
        introspection.update_health("engine3", True)
        
        health = introspection.get_health_status()
        assert health["total_count"] == 3
        assert health["healthy_count"] == 2
        assert health["overall_healthy"] is False
        assert health["health_percentage"] == pytest.approx(66.67, rel=0.1)
    
    def test_heartbeat(self):
        """Test heartbeat recording"""
        from bridge_backend.genesis.introspection import GenesisIntrospection
        
        introspection = GenesisIntrospection()
        
        introspection.heartbeat()
        
        heartbeat = introspection.get_heartbeat_status()
        assert heartbeat["last_heartbeat"] is not None
    
    def test_echo_report(self):
        """Test echo report generation"""
        from bridge_backend.genesis.introspection import GenesisIntrospection
        
        introspection = GenesisIntrospection()
        introspection.update_health("test_engine", True)
        introspection.heartbeat()
        
        report = introspection.generate_echo_report()
        assert report["type"] == "genesis.echo.report"
        assert "health" in report
        assert "heartbeat" in report
        assert "metrics" in report


class TestGenesisOrchestrator:
    """Test Genesis orchestration loop"""
    
    @pytest.mark.asyncio
    async def test_orchestrator_initialization(self):
        """Test orchestrator initializes correctly"""
        from bridge_backend.genesis.orchestration import GenesisOrchestrator
        
        orchestrator = GenesisOrchestrator()
        status = orchestrator.get_status()
        assert status["running"] is False
    
    @pytest.mark.asyncio
    async def test_orchestrator_start_stop(self):
        """Test orchestrator start and stop"""
        from bridge_backend.genesis.orchestration import GenesisOrchestrator
        
        orchestrator = GenesisOrchestrator()
        
        await orchestrator.start()
        await asyncio.sleep(0.1)  # Let it run briefly
        
        status = orchestrator.get_status()
        assert status["running"] is True
        
        await orchestrator.stop()
        await asyncio.sleep(0.1)
        
        status = orchestrator.get_status()
        assert status["running"] is False
    
    @pytest.mark.asyncio
    async def test_action_execution(self):
        """Test action execution"""
        from bridge_backend.genesis.orchestration import GenesisOrchestrator
        
        orchestrator = GenesisOrchestrator()
        
        result = await orchestrator.execute_action("test_action", {"param": "value"})
        assert result["action"] == "test_action"
        assert result["params"]["param"] == "value"


class TestGenesisLinkAdapters:
    """Test Genesis link adapters"""
    
    @pytest.mark.asyncio
    async def test_register_all_links(self):
        """Test registration of all engine links"""
        from bridge_backend.bridge_core.engines.adapters.genesis_link import register_all_genesis_links
        
        # This should not raise an error
        await register_all_genesis_links()


class TestGenesisIntegration:
    """Integration tests for Genesis framework"""
    
    @pytest.mark.asyncio
    async def test_full_genesis_flow(self):
        """Test complete Genesis event flow"""
        from bridge_backend.genesis.bus import genesis_bus
        from bridge_backend.genesis.manifest import genesis_manifest
        from bridge_backend.genesis.introspection import genesis_introspection
        
        # Register a test engine
        genesis_manifest.register_engine("test_engine", {
            "genesis_role": "Test",
            "topics": ["genesis.intent"],
            "dependencies": [],
        })
        
        # Update health
        genesis_introspection.update_health("test_engine", True)
        
        # Subscribe to events
        received = []
        genesis_bus.subscribe("genesis.intent", lambda e: received.append(e))
        
        # Publish event
        await genesis_bus.publish("genesis.intent", {
            "type": "test.integration",
            "data": "integration_test"
        })
        
        # Verify
        assert len(received) == 1
        assert received[0]["type"] == "test.integration"
        
        # Check health
        health = genesis_introspection.get_health_status()
        assert health["overall_healthy"] is True
    
    @pytest.mark.asyncio
    async def test_cross_engine_communication(self):
        """Test communication between multiple engines via Genesis bus"""
        from bridge_backend.genesis.bus import genesis_bus
        
        events_received = {
            "tde_x": [],
            "cascade": [],
            "truth": [],
        }
        
        # Simulate engine subscriptions
        genesis_bus.subscribe("genesis.intent", lambda e: events_received["tde_x"].append(e))
        genesis_bus.subscribe("genesis.fact", lambda e: events_received["truth"].append(e))
        genesis_bus.subscribe("genesis.intent", lambda e: events_received["cascade"].append(e))
        
        # Publish events from different engines
        await genesis_bus.publish("genesis.intent", {
            "type": "tde.signal",
            "source": "tde_x"
        })
        
        await genesis_bus.publish("genesis.fact", {
            "type": "truth.certified",
            "source": "truth"
        })
        
        # Verify cross-engine communication
        assert len(events_received["tde_x"]) == 1
        assert len(events_received["cascade"]) == 1
        assert len(events_received["truth"]) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
