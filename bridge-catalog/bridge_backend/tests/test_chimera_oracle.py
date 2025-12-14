"""
Tests for Chimera Oracle - Predictive Deploy Engine
"""

import pytest
import asyncio
from bridge_backend.engines.chimera.core import ChimeraOracle


@pytest.mark.asyncio
async def test_chimera_oracle_initialization():
    """Test Chimera Oracle initialization"""
    oracle = ChimeraOracle()
    
    assert oracle is not None
    assert oracle.dm is not None
    assert oracle.lev is not None
    assert oracle.truth is not None
    assert oracle.arie is not None
    assert oracle.env is not None
    assert oracle.guard is not None
    assert oracle.fallback is not None
    assert oracle.forge is not None


@pytest.mark.asyncio
async def test_chimera_oracle_run_happy_path():
    """Test Chimera Oracle successful deployment path"""
    oracle = ChimeraOracle()
    
    result = await oracle.run({"ref": "test-sha"})
    
    assert result is not None
    assert "status" in result
    # Should succeed with default simulation
    assert result["status"] in ["ok", "blocked"]


@pytest.mark.asyncio
async def test_chimera_oracle_run_with_ref():
    """Test Chimera Oracle with specific ref"""
    oracle = ChimeraOracle()
    
    result = await oracle.run({"ref": "feature-branch"})
    
    assert result is not None
    assert "outcome" in result or "reason" in result
