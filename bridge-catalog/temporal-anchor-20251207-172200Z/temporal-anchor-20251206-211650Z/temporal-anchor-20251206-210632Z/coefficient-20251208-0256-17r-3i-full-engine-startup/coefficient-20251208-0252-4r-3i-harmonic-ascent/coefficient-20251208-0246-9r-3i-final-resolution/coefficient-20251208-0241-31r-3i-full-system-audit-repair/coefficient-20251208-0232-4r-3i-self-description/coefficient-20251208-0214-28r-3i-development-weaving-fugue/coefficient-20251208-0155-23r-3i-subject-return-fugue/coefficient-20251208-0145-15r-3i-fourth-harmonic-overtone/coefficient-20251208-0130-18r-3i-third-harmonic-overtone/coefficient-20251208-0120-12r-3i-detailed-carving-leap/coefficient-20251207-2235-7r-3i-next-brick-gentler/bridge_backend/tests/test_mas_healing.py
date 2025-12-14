"""
Test MAS Self-Healing
"""

import pytest
import asyncio
from bridge_core.heritage.mas.adapters import (
    BridgeMASAdapter,
    SelfHealingMASAdapter
)


@pytest.mark.asyncio
async def test_healing_valid_message():
    """Test healing with valid message"""
    log = []
    
    def write(m):
        log.append(m)
    
    mas = BridgeMASAdapter(bridge=None, order_write=write)
    heal = SelfHealingMASAdapter(mas, retry_delay=0.01, max_retries=1)
    
    # Valid message
    await heal.handle_incoming({
        "event_type": "test",
        "task_id": "t1",
        "timestamp": "2024-01-01T00:00:00Z"
    })
    
    # Should have written the message
    assert len(log) > 0


@pytest.mark.asyncio
async def test_healing_invalid_message():
    """Test healing with invalid message - triggers resend request"""
    log = []
    
    def write(m):
        log.append(m)
    
    mas = BridgeMASAdapter(bridge=None, order_write=write)
    heal = SelfHealingMASAdapter(mas, retry_delay=0.01, max_retries=1)
    
    # Invalid message (missing required fields)
    await heal.handle_incoming({"bad": "msg"})
    
    # Should have requested resend
    assert any(m.get("type") == "resend_request" for m in log)


@pytest.mark.asyncio
async def test_mas_adapter_event_handling():
    """Test MAS adapter handles events"""
    log = []
    
    def write(m):
        log.append(m)
    
    mas = BridgeMASAdapter(bridge=None, order_write=write)
    
    await mas.handle_bridge_event({
        "event_type": "task.start",
        "task_id": "t1",
        "timestamp": "2024-01-01T00:00:00Z",
        "agent": "agent-1",
        "payload": {"data": "test"}
    })
    
    # Should have written to log
    assert len(log) == 1
    assert log[0]["task_id"] == "t1"
