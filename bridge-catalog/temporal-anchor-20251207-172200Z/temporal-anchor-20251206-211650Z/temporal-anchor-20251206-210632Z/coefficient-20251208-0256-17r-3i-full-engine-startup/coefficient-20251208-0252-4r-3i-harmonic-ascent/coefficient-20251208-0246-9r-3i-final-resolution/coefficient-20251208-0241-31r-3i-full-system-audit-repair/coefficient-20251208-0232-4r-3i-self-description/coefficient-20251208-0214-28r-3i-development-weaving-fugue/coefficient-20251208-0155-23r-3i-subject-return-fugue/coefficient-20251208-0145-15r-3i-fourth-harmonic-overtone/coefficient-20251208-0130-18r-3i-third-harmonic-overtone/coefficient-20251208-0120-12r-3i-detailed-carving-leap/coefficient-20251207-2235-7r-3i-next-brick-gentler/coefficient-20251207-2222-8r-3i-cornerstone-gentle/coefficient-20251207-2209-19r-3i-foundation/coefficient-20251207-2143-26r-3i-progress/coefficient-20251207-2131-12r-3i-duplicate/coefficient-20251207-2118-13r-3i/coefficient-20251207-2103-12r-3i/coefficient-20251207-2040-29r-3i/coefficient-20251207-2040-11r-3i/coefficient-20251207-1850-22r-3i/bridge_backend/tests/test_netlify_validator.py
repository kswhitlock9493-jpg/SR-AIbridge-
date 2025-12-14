"""
Tests for Netlify Validator Engine
"""

import pytest
import asyncio
from bridge_backend.engines.netlify_validator import NetlifyValidator


@pytest.mark.asyncio
async def test_netlify_validator_initialization():
    """Test Netlify Validator initialization"""
    validator = NetlifyValidator()
    
    assert validator is not None
    assert validator.enabled is True


@pytest.mark.asyncio
async def test_validate_rules():
    """Test basic rule validation"""
    validator = NetlifyValidator()
    
    result = await validator.validate_rules()
    
    assert result is not None
    assert "status" in result
    assert "timestamp" in result
    assert result["status"] in ["success", "failed", "error"]


@pytest.mark.asyncio
async def test_validate_rules_with_memory():
    """Test validation with Umbra Memory integration"""
    from bridge_backend.bridge_core.engines.umbra.memory import UmbraMemory
    
    memory = UmbraMemory()
    validator = NetlifyValidator(umbra_memory=memory)
    
    result = await validator.validate_rules()
    
    assert result is not None
    assert "status" in result
    
    # Check if result was recorded to memory
    experiences = await memory.recall(category="netlify_validation", limit=5)
    assert len(experiences) > 0


@pytest.mark.asyncio
async def test_validate_with_recall():
    """Test validation with recall functionality"""
    from bridge_backend.bridge_core.engines.umbra.memory import UmbraMemory
    
    memory = UmbraMemory()
    validator = NetlifyValidator(umbra_memory=memory)
    
    # First validation (will be recorded)
    result1 = await validator.validate_with_recall()
    
    assert result1 is not None
    assert "status" in result1
    
    # Second validation (should recall first one)
    result2 = await validator.validate_with_recall()
    
    assert result2 is not None
    # If first validation succeeded, recall should show at least one experience
    if result1["status"] == "success":
        experiences = await memory.recall(category="netlify_validation")
        assert len(experiences) >= 1


@pytest.mark.asyncio
async def test_validator_metrics():
    """Test validator metrics retrieval"""
    validator = NetlifyValidator()
    
    metrics = validator.get_metrics()
    
    assert metrics is not None
    assert "enabled" in metrics
    assert "truth_available" in metrics
    assert "memory_available" in metrics


@pytest.mark.asyncio
async def test_standalone_validate_function():
    """Test standalone validate_netlify_rules function"""
    from bridge_backend.engines.netlify_validator import validate_netlify_rules
    
    result = validate_netlify_rules()
    
    assert result is not None
    assert "status" in result
    assert result["status"] in ["success", "failed"]
