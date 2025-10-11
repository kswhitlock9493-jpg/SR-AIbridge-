"""
Tests for Env Steward Engine
Admiral-tier environment orchestration
"""

import pytest
from bridge_backend.bridge_core.middleware.permissions import ROLE_MATRIX


def test_rbac_admiral_has_steward_access():
    """Test that admiral role has steward access"""
    admiral_perms = ROLE_MATRIX.get("admiral", {})
    assert admiral_perms.get("steward.read") is True
    assert admiral_perms.get("steward.cap.issue") is True
    assert admiral_perms.get("steward.write") is True


def test_rbac_captain_no_steward_access():
    """Test that captain role does NOT have steward access"""
    captain_perms = ROLE_MATRIX.get("captain", {})
    # Captains should not have steward permissions
    assert captain_perms.get("steward.read", False) is False
    assert captain_perms.get("steward.cap.issue", False) is False
    assert captain_perms.get("steward.write", False) is False


def test_rbac_agent_no_steward_access():
    """Test that agent role does NOT have steward access"""
    agent_perms = ROLE_MATRIX.get("agent", {})
    # Agents should not have steward permissions
    assert agent_perms.get("steward.read", False) is False
    assert agent_perms.get("steward.cap.issue", False) is False
    assert agent_perms.get("steward.write", False) is False


def test_steward_models_import():
    """Test that steward models can be imported"""
    from bridge_backend.engines.steward.models import (
        DiffReport,
        Plan,
        ApplyResult,
        EnvVarChange,
        PlanRequest,
        ApplyRequest
    )
    
    # Create a simple DiffReport
    report = DiffReport(
        has_drift=False,
        providers=["render"]
    )
    assert report.has_drift is False
    assert report.providers == ["render"]


def test_steward_core_import():
    """Test that steward core can be imported"""
    from bridge_backend.engines.steward.core import steward
    
    # Check steward instance exists
    assert steward is not None


def test_steward_adapters_import():
    """Test that steward adapters can be imported"""
    from bridge_backend.engines.steward.adapters import (
        get_adapters,
        RenderAdapter,
        NetlifyAdapter,
        GithubAdapter
    )
    
    # Test adapter instances
    render = RenderAdapter()
    assert render.name == "render"
    
    netlify = NetlifyAdapter()
    assert netlify.name == "netlify"
    
    github = GithubAdapter()
    assert github.name == "github"


def test_genesis_steward_topics():
    """Test that Genesis bus has steward topics"""
    from bridge_backend.genesis.bus import GenesisEventBus
    
    bus = GenesisEventBus()
    
    # Check that steward topics are registered
    assert "steward.intent" in bus._valid_topics
    assert "steward.plan" in bus._valid_topics
    assert "steward.apply" in bus._valid_topics
    assert "steward.result" in bus._valid_topics
    assert "steward.rollback" in bus._valid_topics
    assert "steward.cap.issued" in bus._valid_topics


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
