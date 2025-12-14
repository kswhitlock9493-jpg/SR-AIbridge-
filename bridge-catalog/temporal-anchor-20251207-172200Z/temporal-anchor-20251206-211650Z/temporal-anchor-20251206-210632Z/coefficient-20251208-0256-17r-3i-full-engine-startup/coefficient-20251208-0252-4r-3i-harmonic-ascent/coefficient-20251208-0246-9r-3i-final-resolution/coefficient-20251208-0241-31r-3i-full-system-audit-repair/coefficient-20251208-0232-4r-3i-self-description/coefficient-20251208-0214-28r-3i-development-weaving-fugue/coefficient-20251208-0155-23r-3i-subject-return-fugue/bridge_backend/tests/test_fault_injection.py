"""
Test Fault Injection
"""

import pytest
from bridge_core.heritage.mas.fault_injector import FaultInjector


def test_fault_injector_no_faults():
    """Test fault injector with all rates at 0"""
    sink = []
    
    def write(m):
        sink.append(m)
    
    fi = FaultInjector(
        base_write=write,
        corrupt_rate=0.0,
        delay_rate=0.0,
        reorder_rate=0.0,
        drop_rate=0.0
    )
    
    import asyncio
    asyncio.run(fi({"type": "log", "task_id": "t1"}))
    
    assert len(sink) == 1
    assert sink[0]["task_id"] == "t1"


def test_fault_injector_corrupt():
    """Test corruption fault injection"""
    sink = []
    
    def write(m):
        sink.append(m)
    
    fi = FaultInjector(
        base_write=write,
        corrupt_rate=1.0,  # Always corrupt
        delay_rate=0.0,
        reorder_rate=0.0,
        drop_rate=0.0
    )
    
    import asyncio
    asyncio.run(fi({"type": "log", "task_id": "t1", "payload": {}}))
    
    assert len(sink) == 1
    # Message should be corrupted
    assert "_corrupted" in sink[0].get("payload", {})


def test_fault_injector_drop():
    """Test drop fault injection"""
    sink = []
    
    def write(m):
        sink.append(m)
    
    fi = FaultInjector(
        base_write=write,
        corrupt_rate=0.0,
        delay_rate=0.0,
        reorder_rate=0.0,
        drop_rate=1.0  # Always drop
    )
    
    import asyncio
    asyncio.run(fi({"type": "log", "task_id": "t1"}))
    
    # Message should be dropped
    assert len(sink) == 0
