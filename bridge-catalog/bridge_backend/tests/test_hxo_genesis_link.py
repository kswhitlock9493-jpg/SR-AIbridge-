"""
Tests for HXO Genesis Link v1.9.6q
Tests async-safe registration with both sync and async bus implementations
"""
import asyncio
import pytest
from bridge_backend.bridge_core.engines.adapters.hxo_genesis_link import HXOGenesisLink


class DummyBus:
    def __init__(self, async_mode=False):
        self.subs = {}
        self.async_mode = async_mode

    async def _subscribe_async(self, topic, cb):
        self.subs[topic] = cb
    
    def _subscribe_sync(self, topic, cb):
        self.subs[topic] = cb

    def subscribe(self, topic, cb):
        if self.async_mode:
            return self._subscribe_async(topic, cb)
        return self._subscribe_sync(topic, cb)


class DummyHXO:
    async def handle_genesis_heal(self, e):
        pass
    
    async def on_tde_completed(self, e):
        pass
    
    async def on_tde_failed(self, e):
        pass


@pytest.mark.asyncio
@pytest.mark.parametrize("async_mode", (False, True))
async def test_register_tolerates_sync_and_async(async_mode):
    """Test that HXOGenesisLink handles both sync and async bus.subscribe()"""
    bus = DummyBus(async_mode=async_mode)
    hxo = DummyHXO()
    link = HXOGenesisLink(bus, hxo)
    
    await link.register()
    
    # Verify subscriptions were registered
    assert "genesis.heal" in bus.subs
    assert "deploy.tde.orchestrator.completed" in bus.subs
    assert "deploy.tde.orchestrator.failed" in bus.subs


@pytest.mark.asyncio
async def test_register_is_idempotent():
    """Test that calling register() multiple times is safe"""
    bus = DummyBus(async_mode=False)
    hxo = DummyHXO()
    link = HXOGenesisLink(bus, hxo)
    
    # Register multiple times
    await link.register()
    await link.register()
    await link.register()
    
    # Should still have the subscriptions
    assert "genesis.heal" in bus.subs
    assert "deploy.tde.orchestrator.completed" in bus.subs
    assert "deploy.tde.orchestrator.failed" in bus.subs
