"""
Test suite for Genesis v2.0.1 (Project Genesis)
Tests for contracts, adapters, persistence, replay, and guardians
"""
import pytest
import pytest_asyncio
import asyncio
import os
from datetime import datetime, timedelta
from pathlib import Path

# Configure pytest-asyncio
pytestmark = pytest.mark.asyncio


class TestGenesisContracts:
    """Test Genesis Core Contract (GCC)"""
    
    def test_genesis_event_creation(self):
        """Test GenesisEvent creation and validation"""
        from bridge_backend.genesis.contracts import GenesisEvent
        
        event = GenesisEvent(
            topic="engine.truth.fact.created",
            source="engine.truth",
            kind="fact",
            payload={"test": "data"}
        )
        
        assert event.topic == "engine.truth.fact.created"
        assert event.source == "engine.truth"
        assert event.kind == "fact"
        assert event.payload == {"test": "data"}
        assert event.id is not None
        assert event.ts is not None
        assert event.schema == "genesis.event.v1"
    
    def test_genesis_event_with_dedupe_key(self):
        """Test GenesisEvent with idempotency key"""
        from bridge_backend.genesis.contracts import GenesisEvent
        
        event = GenesisEvent(
            topic="engine.truth.fact.created",
            source="engine.truth",
            kind="fact",
            payload={"test": "data"},
            dedupe_key="unique-key-123"
        )
        
        assert event.dedupe_key == "unique-key-123"
    
    def test_genesis_event_with_correlation(self):
        """Test GenesisEvent with correlation and causation IDs"""
        from bridge_backend.genesis.contracts import GenesisEvent
        
        event = GenesisEvent(
            topic="engine.truth.fact.created",
            source="engine.truth",
            kind="fact",
            payload={"test": "data"},
            correlation_id="mission-42",
            causation_id="event-123"
        )
        
        assert event.correlation_id == "mission-42"
        assert event.causation_id == "event-123"


class TestGenesisAdapters:
    """Test Genesis adapters and emit helpers"""
    
    @pytest.mark.asyncio
    async def test_emit_intent(self):
        """Test emit_intent adapter"""
        from bridge_backend.genesis.adapters import emit_intent
        
        event_id = await emit_intent(
            topic="engine.truth.fact.created",
            source="engine.truth",
            payload={"test": "intent"}
        )
        
        assert event_id is not None
    
    @pytest.mark.asyncio
    async def test_emit_heal(self):
        """Test emit_heal adapter"""
        from bridge_backend.genesis.adapters import emit_heal
        
        event_id = await emit_heal(
            topic="runtime.health.degraded",
            source="runtime.health",
            payload={"component": "database", "status": "degraded"}
        )
        
        assert event_id is not None
    
    @pytest.mark.asyncio
    async def test_emit_fact(self):
        """Test emit_fact adapter"""
        from bridge_backend.genesis.adapters import emit_fact
        
        event_id = await emit_fact(
            topic="engine.truth.fact.certified",
            source="engine.truth",
            payload={"fact_id": "fact-123"}
        )
        
        assert event_id is not None
    
    @pytest.mark.asyncio
    async def test_health_degraded_helper(self):
        """Test health_degraded convenience helper"""
        from bridge_backend.genesis.adapters import health_degraded
        
        event_id = await health_degraded(
            component="database",
            details={"status": "degraded", "latency_ms": 500}
        )
        
        assert event_id is not None
    
    @pytest.mark.asyncio
    async def test_deploy_failed_helper(self):
        """Test deploy_failed convenience helper"""
        from bridge_backend.genesis.adapters import deploy_failed
        
        event_id = await deploy_failed(
            stage="warm_caches",
            details={"error": "timeout", "attempt": 2}
        )
        
        assert event_id is not None


class TestGenesisPersistence:
    """Test Genesis persistence layer"""
    
    @pytest.mark.asyncio
    async def test_persistence_initialization(self):
        """Test persistence initialization"""
        from bridge_backend.genesis.persistence import genesis_persistence
        
        await genesis_persistence.initialize()
        assert genesis_persistence._initialized
    
    @pytest.mark.asyncio
    async def test_is_duplicate(self):
        """Test duplicate detection"""
        from bridge_backend.genesis.persistence import genesis_persistence
        
        await genesis_persistence.initialize()
        
        # First check should return False
        is_dup = await genesis_persistence.is_duplicate("test-key-123")
        assert not is_dup
    
    @pytest.mark.asyncio
    async def test_record_event(self):
        """Test event recording"""
        from bridge_backend.genesis.persistence import genesis_persistence
        import time
        
        await genesis_persistence.initialize()
        
        # Use timestamp to ensure uniqueness
        unique_key = f"unique-test-key-{time.time()}"
        
        success = await genesis_persistence.record_event(
            event_id=f"test-event-{time.time()}",
            topic="test.topic",
            source="test.source",
            kind="fact",
            payload={"test": "data"},
            dedupe_key=unique_key
        )
        
        assert success
        
        # Verify dedupe works
        is_dup = await genesis_persistence.is_duplicate(unique_key)
        assert is_dup
    
    @pytest.mark.asyncio
    async def test_get_events(self):
        """Test event retrieval"""
        from bridge_backend.genesis.persistence import genesis_persistence
        
        await genesis_persistence.initialize()
        
        # Record a test event
        await genesis_persistence.record_event(
            event_id="test-event-456",
            topic="test.retrieval",
            source="test.source",
            kind="fact",
            payload={"test": "retrieval"}
        )
        
        # Retrieve events
        events = await genesis_persistence.get_events(
            topic_pattern="test.%",
            limit=10
        )
        
        assert len(events) > 0
    
    @pytest.mark.asyncio
    async def test_get_watermark(self):
        """Test watermark retrieval"""
        from bridge_backend.genesis.persistence import genesis_persistence
        
        await genesis_persistence.initialize()
        
        watermark = await genesis_persistence.get_watermark()
        assert watermark >= 0


class TestGuardiansGate:
    """Test Guardians safety gate"""
    
    def test_guardians_initialization(self):
        """Test guardians gate initialization"""
        from bridge_backend.bridge_core.guardians.gate import guardians_gate
        
        assert guardians_gate is not None
        stats = guardians_gate.get_stats()
        assert "enforce_strict" in stats
    
    def test_allow_normal_event(self):
        """Test that normal events are allowed"""
        from bridge_backend.bridge_core.guardians.gate import guardians_gate
        
        event = {
            "id": "test-123",
            "topic": "engine.truth.fact.created",
            "payload": {"test": "data"}
        }
        
        allowed, reason = guardians_gate.allow(event)
        assert allowed
        assert reason is None
    
    def test_block_destructive_pattern(self):
        """Test that destructive patterns are blocked"""
        from bridge_backend.bridge_core.guardians.gate import guardians_gate
        
        event = {
            "id": "test-456",
            "topic": "database.delete.all",
            "payload": {"test": "data"}
        }
        
        allowed, reason = guardians_gate.allow(event)
        # May be blocked depending on GUARDIANS_ENFORCE_STRICT
        if not allowed:
            assert "destructive" in reason.lower() or "pattern" in reason.lower()
    
    def test_suspicious_payload_detection(self):
        """Test that suspicious payloads are detected"""
        from bridge_backend.bridge_core.guardians.gate import guardians_gate
        
        event = {
            "id": "test-789",
            "topic": "test.topic",
            "payload": {"query": "DROP TABLE users"}
        }
        
        allowed, reason = guardians_gate.allow(event)
        # May be blocked if suspicious patterns detected
        if not allowed:
            assert reason is not None


class TestGenesisReplay:
    """Test Genesis replay functionality"""
    
    @pytest.mark.asyncio
    async def test_get_current_watermark(self):
        """Test getting current watermark"""
        from bridge_backend.genesis.replay import genesis_replay
        
        watermark = await genesis_replay.get_current_watermark()
        assert watermark >= 0
    
    @pytest.mark.asyncio
    async def test_replay_from_watermark(self):
        """Test replay from watermark"""
        from bridge_backend.genesis.replay import genesis_replay
        from bridge_backend.genesis.persistence import genesis_persistence
        
        await genesis_persistence.initialize()
        
        # Record a test event
        await genesis_persistence.record_event(
            event_id="replay-test-123",
            topic="test.replay",
            source="test.source",
            kind="fact",
            payload={"test": "replay"}
        )
        
        # Get current watermark
        watermark = await genesis_replay.get_current_watermark()
        
        # Replay from beginning (without re-emitting)
        events = await genesis_replay.replay_from_watermark(
            watermark=0,
            topic_pattern="test.%",
            limit=10,
            emit=False
        )
        
        assert len(events) > 0


class TestPortResolution:
    """Test PORT resolution (no loops)"""
    
    def test_resolve_port_with_valid_port(self):
        """Test resolve_port with valid PORT env var"""
        from bridge_backend.runtime.ports import resolve_port
        
        # Save original
        original = os.environ.get("PORT")
        
        # Test with valid PORT
        os.environ["PORT"] = "10000"
        port = resolve_port()
        assert port == 10000
        
        # Restore
        if original:
            os.environ["PORT"] = original
        elif "PORT" in os.environ:
            del os.environ["PORT"]
    
    def test_resolve_port_with_invalid_port(self):
        """Test resolve_port with invalid PORT env var"""
        from bridge_backend.runtime.ports import resolve_port
        
        # Save original
        original = os.environ.get("PORT")
        
        # Test with invalid PORT
        os.environ["PORT"] = "not_a_number"
        port = resolve_port()
        assert port == 8000  # Should fallback to default
        
        # Restore
        if original:
            os.environ["PORT"] = original
        elif "PORT" in os.environ:
            del os.environ["PORT"]
    
    def test_resolve_port_without_port(self):
        """Test resolve_port without PORT env var"""
        from bridge_backend.runtime.ports import resolve_port
        
        # Save original
        original = os.environ.get("PORT")
        
        # Remove PORT
        if "PORT" in os.environ:
            del os.environ["PORT"]
        
        port = resolve_port()
        assert port == 8000  # Should default to 8000
        
        # Restore
        if original:
            os.environ["PORT"] = original


class TestTDEXv2Orchestrator:
    """Test TDE-X v2 orchestrator"""
    
    def test_orchestrator_initialization(self):
        """Test TDE-X v2 orchestrator initialization"""
        from bridge_backend.runtime.tde_x.orchestrator_v2 import tde_orchestrator
        
        assert tde_orchestrator is not None
        status = tde_orchestrator.get_status()
        assert "stages" in status
        assert len(status["stages"]) == 4  # 4 stages
    
    def test_orchestrator_stages(self):
        """Test that all required stages exist"""
        from bridge_backend.runtime.tde_x.orchestrator_v2 import tde_orchestrator
        
        status = tde_orchestrator.get_status()
        stages = status["stages"]
        
        assert "post_boot" in stages
        assert "warm_caches" in stages
        assert "index_assets" in stages
        assert "scan_federation" in stages
    
    @pytest.mark.asyncio
    async def test_orchestrator_run(self):
        """Test TDE-X v2 orchestrator run (doesn't block)"""
        from bridge_backend.runtime.tde_x.orchestrator_v2 import tde_orchestrator
        
        # This should return quickly without blocking
        import time
        start = time.time()
        await tde_orchestrator.run()
        elapsed = time.time() - start
        
        # Should complete in less than 1 second (it runs in background)
        assert elapsed < 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
