"""
Test Autonomy Engine Integration with Triage, Federation, and Parity
"""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from pathlib import Path


@pytest.mark.asyncio
async def test_autonomy_subscribes_to_triage_events():
    """Test that autonomy engine subscribes to triage events"""
    with patch('bridge_backend.bridge_core.engines.adapters.genesis_link.genesis_bus') as mock_bus:
        mock_bus.is_enabled.return_value = True
        mock_bus.subscribe = Mock()
        
        from bridge_backend.bridge_core.engines.adapters.genesis_link import _register_autonomy_link
        
        await _register_autonomy_link()
        
        # Verify subscribe was called with triage topics
        call_topics = [call[0][0] for call in mock_bus.subscribe.call_args_list]
        
        assert "triage.api" in call_topics
        assert "triage.endpoint" in call_topics
        assert "triage.diagnostics" in call_topics
        print("✅ Autonomy subscribes to all triage topics")


@pytest.mark.asyncio
async def test_autonomy_subscribes_to_federation_events():
    """Test that autonomy engine subscribes to federation events"""
    with patch('bridge_backend.bridge_core.engines.adapters.genesis_link.genesis_bus') as mock_bus:
        mock_bus.is_enabled.return_value = True
        mock_bus.subscribe = Mock()
        
        from bridge_backend.bridge_core.engines.adapters.genesis_link import _register_autonomy_link
        
        await _register_autonomy_link()
        
        # Verify subscribe was called with federation topics
        call_topics = [call[0][0] for call in mock_bus.subscribe.call_args_list]
        
        assert "federation.events" in call_topics
        assert "federation.heartbeat" in call_topics
        print("✅ Autonomy subscribes to all federation topics")


@pytest.mark.asyncio
async def test_autonomy_subscribes_to_parity_events():
    """Test that autonomy engine subscribes to parity events"""
    with patch('bridge_backend.bridge_core.engines.adapters.genesis_link.genesis_bus') as mock_bus:
        mock_bus.is_enabled.return_value = True
        mock_bus.subscribe = Mock()
        
        from bridge_backend.bridge_core.engines.adapters.genesis_link import _register_autonomy_link
        
        await _register_autonomy_link()
        
        # Verify subscribe was called with parity topics
        call_topics = [call[0][0] for call in mock_bus.subscribe.call_args_list]
        
        assert "parity.check" in call_topics
        assert "parity.autofix" in call_topics
        print("✅ Autonomy subscribes to all parity topics")


def test_genesis_bus_includes_new_topics():
    """Test that genesis bus includes new topics for autonomy integration"""
    import sys
    import os
    
    # Add bridge_backend to path
    backend_path = Path(__file__).parent.parent
    if str(backend_path) not in sys.path:
        sys.path.insert(0, str(backend_path))
    
    # Set required env vars
    os.environ.setdefault("DATABASE_URL", "test")
    os.environ.setdefault("SECRET_KEY", "test")
    
    from genesis.bus import GenesisEventBus
    
    bus = GenesisEventBus()
    
    # Check that new topics are in valid topics
    required_topics = {
        "triage.api",
        "triage.endpoint", 
        "triage.diagnostics",
        "federation.events",
        "federation.heartbeat",
        "parity.check",
        "parity.autofix"
    }
    
    for topic in required_topics:
        assert topic in bus._valid_topics, f"Topic {topic} not in valid topics"
    
    print("✅ All integration topics registered in genesis bus")


if __name__ == "__main__":
    # Run tests
    asyncio.run(test_autonomy_subscribes_to_triage_events())
    asyncio.run(test_autonomy_subscribes_to_federation_events())
    asyncio.run(test_autonomy_subscribes_to_parity_events())
    test_genesis_bus_includes_new_topics()
    print("\n" + "="*60)
    print("✅ All autonomy integration tests passed!")
    print("="*60)
