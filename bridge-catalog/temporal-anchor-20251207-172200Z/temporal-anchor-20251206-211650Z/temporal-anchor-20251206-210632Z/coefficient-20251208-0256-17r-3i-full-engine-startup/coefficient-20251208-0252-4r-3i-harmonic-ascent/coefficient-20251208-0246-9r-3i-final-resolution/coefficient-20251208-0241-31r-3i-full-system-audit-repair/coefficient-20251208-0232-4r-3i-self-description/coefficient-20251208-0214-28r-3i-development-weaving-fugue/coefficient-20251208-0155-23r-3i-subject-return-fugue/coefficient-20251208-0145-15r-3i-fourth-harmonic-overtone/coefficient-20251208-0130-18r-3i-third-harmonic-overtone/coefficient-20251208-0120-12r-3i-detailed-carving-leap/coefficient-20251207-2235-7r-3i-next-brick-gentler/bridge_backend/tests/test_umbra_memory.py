"""
Tests for Umbra Memory - Experience Graph & Recall Engine
"""

import pytest
import asyncio
from datetime import datetime, timezone
from bridge_backend.bridge_core.engines.umbra.memory import UmbraMemory


@pytest.mark.asyncio
async def test_umbra_memory_initialization():
    """Test Umbra Memory initialization"""
    memory = UmbraMemory()
    
    assert memory is not None
    assert memory.enabled is True
    assert isinstance(memory.experiences, list)


@pytest.mark.asyncio
async def test_record_experience():
    """Test recording an experience"""
    memory = UmbraMemory()
    
    data = {
        "anomaly_id": "high_error_rate",
        "actions": [{"action": "restart"}],
        "confidence": 0.85
    }
    
    result = {"success": True}
    
    entry = await memory.record("repair", data, result)
    
    assert entry is not None
    assert entry["category"] == "repair"
    assert entry["data"] == data
    assert entry["result"] == result
    assert "id" in entry
    assert "timestamp" in entry


@pytest.mark.asyncio
async def test_recall_all():
    """Test recalling all experiences"""
    memory = UmbraMemory()
    
    # Record some experiences
    await memory.record("repair", {"test": 1})
    await memory.record("anomaly", {"test": 2})
    await memory.record("repair", {"test": 3})
    
    # Recall all
    experiences = await memory.recall()
    
    assert len(experiences) >= 3


@pytest.mark.asyncio
async def test_recall_by_category():
    """Test recalling experiences by category"""
    memory = UmbraMemory()
    
    # Record experiences
    await memory.record("repair", {"test": 1})
    await memory.record("anomaly", {"test": 2})
    await memory.record("repair", {"test": 3})
    
    # Recall only repairs
    repairs = await memory.recall(category="repair")
    
    assert all(e["category"] == "repair" for e in repairs)


@pytest.mark.asyncio
async def test_recall_with_limit():
    """Test recalling with limit"""
    memory = UmbraMemory()
    
    # Record multiple experiences
    for i in range(5):
        await memory.record("test", {"index": i})
    
    # Recall with limit
    experiences = await memory.recall(limit=3)
    
    assert len(experiences) <= 3


@pytest.mark.asyncio
async def test_learn_pattern():
    """Test pattern learning from experiences"""
    memory = UmbraMemory()
    
    # Record repair experiences
    await memory.record("repair", {
        "anomaly_id": "high_error_rate",
        "actions": [{"action": "restart"}],
        "confidence": 0.85
    }, {"success": True})
    
    await memory.record("repair", {
        "anomaly_id": "high_error_rate",
        "actions": [{"action": "restart"}],
        "confidence": 0.90
    }, {"success": True})
    
    await memory.record("repair", {
        "anomaly_id": "high_latency",
        "actions": [{"action": "scale"}],
        "confidence": 0.75
    }, {"success": False})
    
    # Learn patterns
    patterns = await memory.learn_pattern("repair")
    
    assert patterns is not None
    assert "patterns" in patterns
    assert "total_experiences" in patterns
    assert patterns["total_experiences"] >= 3


@pytest.mark.asyncio
async def test_learn_pattern_empty():
    """Test pattern learning with no experiences"""
    memory = UmbraMemory()
    
    patterns = await memory.learn_pattern("nonexistent")
    
    assert patterns is not None
    assert patterns["patterns"] == [] or isinstance(patterns["patterns"], dict)


@pytest.mark.asyncio
async def test_get_metrics():
    """Test metrics retrieval"""
    memory = UmbraMemory()
    
    # Record some experiences
    await memory.record("repair", {"test": 1})
    await memory.record("anomaly", {"test": 2})
    
    metrics = memory.get_metrics()
    
    assert metrics is not None
    assert "enabled" in metrics
    assert "total_experiences" in metrics
    assert "categories" in metrics
    assert metrics["total_experiences"] >= 2


@pytest.mark.asyncio
async def test_memory_persistence():
    """Test that memory persists across instances"""
    # Create first instance and record
    memory1 = UmbraMemory()
    initial_count = len(memory1.experiences)
    
    await memory1.record("test", {"persistent": True})
    
    # Create second instance and check
    memory2 = UmbraMemory()
    
    assert len(memory2.experiences) == initial_count + 1
    
    # Find the test experience
    test_exp = [e for e in memory2.experiences if e.get("data", {}).get("persistent")]
    assert len(test_exp) > 0
