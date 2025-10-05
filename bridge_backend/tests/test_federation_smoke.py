"""
Test Federation smoke tests
"""

import pytest
import asyncio
from bridge_core.heritage.federation.federation_client import FederationClient


@pytest.mark.asyncio
async def test_federation_client_init():
    """Test federation client initialization"""
    client = FederationClient(node_id="test-node")
    
    assert client.node_id == "test-node"
    assert isinstance(client.connected_nodes, dict)


@pytest.mark.asyncio
async def test_federation_forward_task():
    """Test task forwarding"""
    client = FederationClient(node_id="test-node")
    
    result = await client.forward_task(
        task_id="t1",
        task_type="analysis",
        payload={"data": "test"},
        target_node="remote-node"
    )
    
    assert result["status"] == "forwarded"
    assert result["task_id"] == "t1"


@pytest.mark.asyncio
async def test_federation_heartbeat():
    """Test heartbeat sending"""
    client = FederationClient(node_id="test-node")
    
    # Should not raise
    await client.send_heartbeat(["node-1", "node-2"])


@pytest.mark.asyncio
async def test_federation_ack():
    """Test acknowledgment handling"""
    client = FederationClient(node_id="test-node")
    
    # Should not raise
    await client.handle_ack({
        "from_node": "remote-node",
        "task_id": "t1",
        "status": "received"
    })
