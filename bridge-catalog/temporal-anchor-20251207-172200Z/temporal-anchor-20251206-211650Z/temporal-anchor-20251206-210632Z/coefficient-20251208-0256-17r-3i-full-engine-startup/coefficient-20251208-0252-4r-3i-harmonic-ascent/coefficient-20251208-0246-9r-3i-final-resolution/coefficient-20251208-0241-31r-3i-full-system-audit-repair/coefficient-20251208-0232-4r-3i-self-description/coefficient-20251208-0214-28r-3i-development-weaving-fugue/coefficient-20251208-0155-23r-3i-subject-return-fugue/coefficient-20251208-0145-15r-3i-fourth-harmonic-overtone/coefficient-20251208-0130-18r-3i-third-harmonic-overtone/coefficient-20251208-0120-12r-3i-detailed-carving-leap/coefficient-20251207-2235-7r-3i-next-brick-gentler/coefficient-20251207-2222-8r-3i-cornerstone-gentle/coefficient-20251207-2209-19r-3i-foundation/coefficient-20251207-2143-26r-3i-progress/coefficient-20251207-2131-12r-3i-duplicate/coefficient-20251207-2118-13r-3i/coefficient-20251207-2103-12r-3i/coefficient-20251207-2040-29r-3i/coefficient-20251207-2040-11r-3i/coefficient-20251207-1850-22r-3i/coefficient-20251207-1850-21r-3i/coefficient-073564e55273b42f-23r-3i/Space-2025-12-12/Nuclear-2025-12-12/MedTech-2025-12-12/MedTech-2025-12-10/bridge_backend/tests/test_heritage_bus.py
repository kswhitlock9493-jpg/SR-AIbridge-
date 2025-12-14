"""
Test Heritage Event Bus
"""

import pytest
import asyncio
from bridge_core.heritage.event_bus import bus


@pytest.mark.asyncio
async def test_pubsub_roundtrip():
    """Test basic publish/subscribe"""
    seen = []
    
    def handler(e):
        seen.append(e["x"])
    
    bus.subscribe("test.topic", handler)
    await bus.publish("test.topic", {"x": 42})
    
    # Give event loop time to process
    await asyncio.sleep(0.1)
    
    assert seen == [42]


@pytest.mark.asyncio
async def test_async_handler():
    """Test async event handler"""
    seen = []
    
    async def async_handler(e):
        await asyncio.sleep(0.01)
        seen.append(e["value"])
    
    bus.subscribe("async.topic", async_handler)
    await bus.publish("async.topic", {"value": "test"})
    
    await asyncio.sleep(0.1)
    
    assert seen == ["test"]


@pytest.mark.asyncio
async def test_multiple_subscribers():
    """Test multiple subscribers to same topic"""
    results = []
    
    def handler1(e):
        results.append(("h1", e["data"]))
    
    def handler2(e):
        results.append(("h2", e["data"]))
    
    bus.subscribe("multi.topic", handler1)
    bus.subscribe("multi.topic", handler2)
    
    await bus.publish("multi.topic", {"data": "shared"})
    
    await asyncio.sleep(0.1)
    
    assert len(results) == 2
    assert ("h1", "shared") in results
    assert ("h2", "shared") in results
