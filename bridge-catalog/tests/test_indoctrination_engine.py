"""
Tests for Indoctrination Engine
"""

import pytest
from bridge_backend.bridge_core.engines.indoctrination.service import (
    IndoctrinationEngine,
    IndoctrinationRecord,
    DEFAULT_DOCTRINE,
)


def test_engine_initialization():
    """Test that IndoctrinationEngine initializes correctly"""
    engine = IndoctrinationEngine()
    assert engine is not None
    assert engine._doctrine == DEFAULT_DOCTRINE
    assert engine.ttl.total_seconds() == 24 * 3600


def test_doctrine_structure():
    """Test that default doctrine has required structure"""
    engine = IndoctrinationEngine()
    doctrine = engine.doctrine()
    
    assert "laws" in doctrine
    assert "lore" in doctrine
    assert "resonance_checks" in doctrine
    assert "min_score" in doctrine
    
    assert isinstance(doctrine["laws"], list)
    assert isinstance(doctrine["lore"], list)
    assert isinstance(doctrine["resonance_checks"], list)
    assert len(doctrine["laws"]) >= 3
    assert len(doctrine["resonance_checks"]) >= 2


def test_status_empty():
    """Test status with no records"""
    engine = IndoctrinationEngine()
    status = engine.status()
    
    assert status["records"] == 0
    assert status["passed"] == 0
    assert status["failed"] == 0
    assert "doctrine_version" in status


def test_indoctrination_pass():
    """Test successful indoctrination"""
    engine = IndoctrinationEngine()
    
    answers = {
        "pledge": "I pledge to the Sovereign Bridge",
        "ethic": "I will care for all users"
    }
    
    record = engine.indoctrinate("agent_001", answers)
    
    assert record.agent_id == "agent_001"
    assert record.passed is True
    assert record.score == 2
    assert record.details["pledge"] == "pass"
    assert record.details["ethic"] == "pass"


def test_indoctrination_fail():
    """Test failed indoctrination"""
    engine = IndoctrinationEngine()
    
    # Answers that don't match the regex patterns
    answers = {
        "pledge": "I pledge nothing",
        "ethic": "I don't know"
    }
    
    record = engine.indoctrinate("agent_002", answers)
    
    assert record.agent_id == "agent_002"
    assert record.passed is False
    assert record.score == 0
    assert record.details["pledge"] == "fail"
    assert record.details["ethic"] == "fail"


def test_indoctrination_partial():
    """Test partial indoctrination (one pass, one fail)"""
    engine = IndoctrinationEngine()
    
    answers = {
        "pledge": "I pledge to the Sovereign Bridge",  # Has chars before and after "Sovereign"
        "ethic": "nothing"  # doesn't contain "care"
    }
    
    record = engine.indoctrinate("agent_003", answers)
    
    assert record.agent_id == "agent_003"
    assert record.passed is False  # min_score is 2, only got 1
    assert record.score == 1
    assert record.details["pledge"] == "pass"
    assert record.details["ethic"] == "fail"


def test_get_record():
    """Test retrieving a record"""
    engine = IndoctrinationEngine()
    
    answers = {
        "pledge": "I take the Sovereign pledge",  # Has chars before and after
        "ethic": "I will care for all"  # Has chars before and after
    }
    
    engine.indoctrinate("agent_004", answers)
    
    retrieved = engine.get("agent_004")
    assert retrieved is not None
    assert retrieved.agent_id == "agent_004"
    assert retrieved.passed is True


def test_get_nonexistent_record():
    """Test retrieving a non-existent record"""
    engine = IndoctrinationEngine()
    
    retrieved = engine.get("nonexistent_agent")
    assert retrieved is None


def test_status_with_records():
    """Test status with multiple records"""
    engine = IndoctrinationEngine()
    
    # Pass
    engine.indoctrinate("agent_pass_1", {
        "pledge": "I am Sovereign bound",
        "ethic": "I care deeply"
    })
    
    # Fail
    engine.indoctrinate("agent_fail_1", {
        "pledge": "nope",
        "ethic": "nope"
    })
    
    # Pass
    engine.indoctrinate("agent_pass_2", {
        "pledge": "The Sovereign Bridge beckons",
        "ethic": "I care and serve"
    })
    
    status = engine.status()
    
    assert status["records"] == 3
    assert status["passed"] == 2
    assert status["failed"] == 1


def test_record_overwrite():
    """Test that re-indoctrinating an agent overwrites the record"""
    engine = IndoctrinationEngine()
    
    # First attempt - fail
    engine.indoctrinate("agent_005", {
        "pledge": "no",
        "ethic": "no"
    })
    
    # Second attempt - pass
    engine.indoctrinate("agent_005", {
        "pledge": "I serve the Sovereign well",
        "ethic": "I care for all"
    })
    
    record = engine.get("agent_005")
    assert record.passed is True
    
    status = engine.status()
    assert status["records"] == 1  # Only one record for agent_005


def test_purge_expired():
    """Test that purge_expired doesn't crash (can't easily test expiry without mocking time)"""
    engine = IndoctrinationEngine()
    
    engine.indoctrinate("agent_006", {
        "pledge": "I serve the Sovereign always",
        "ethic": "I care for everyone"
    })
    
    # This should not remove the record since it was just created
    engine.purge_expired()
    
    record = engine.get("agent_006")
    assert record is not None
