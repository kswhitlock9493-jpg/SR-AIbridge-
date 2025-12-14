"""
Tests for Hydra Guard v2
"""

import pytest
import asyncio
from pathlib import Path
from bridge_backend.engines.hydra.guard import HydraGuard


@pytest.mark.asyncio
async def test_hydra_guard_initialization():
    """Test Hydra Guard initialization"""
    guard = HydraGuard()
    
    assert guard is not None


@pytest.mark.asyncio
async def test_hydra_guard_synthesize():
    """Test Hydra Guard synthesis"""
    guard = HydraGuard()
    
    result = await guard.synthesize_and_validate()
    
    assert result is not None
    assert result["ok"] is True
    assert "headers" in result
    assert "redirects" in result
    assert "toml" in result


@pytest.mark.asyncio
async def test_hydra_guard_deploy():
    """Test Hydra Guard deploy method"""
    guard = HydraGuard()
    
    plan = {"target": "netlify", "confidence": "high"}
    result = await guard.deploy(plan)
    
    assert result is not None
    assert result["ok"] is True
    assert result["provider"] == "netlify"
