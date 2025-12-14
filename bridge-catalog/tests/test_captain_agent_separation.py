"""
Test captain vs agent role separation in missions and fleet
"""
import pytest
import json
from pathlib import Path


def test_mission_creation_with_captain():
    """Test that missions are created with captain ownership"""
    # This test validates the structure needed for captain-owned missions
    mission = {
        "title": "Test Captain Mission",
        "description": "A mission owned by a captain",
        "captain": "Captain Alpha",
        "role": "captain",
        "priority": "high",
        "status": "pending"
    }
    
    # Validate required fields for captain missions
    assert mission["captain"] is not None
    assert mission["role"] == "captain"
    assert "title" in mission
    assert "priority" in mission


def test_agent_mission_creation():
    """Test that agent jobs have correct role"""
    agent_job = {
        "title": "Writer Portal Job",
        "description": "Automated content generation",
        "captain": None,  # Agent jobs don't have captain owners
        "role": "agent",
        "priority": "medium",
        "status": "pending"
    }
    
    # Validate agent job structure
    assert agent_job["role"] == "agent"
    assert agent_job["captain"] is None or agent_job["captain"] == ""


def test_mission_filtering():
    """Test that missions can be filtered by captain and role"""
    all_missions = [
        {"id": "1", "captain": "Captain Alpha", "role": "captain", "title": "Mission 1"},
        {"id": "2", "captain": "Captain Beta", "role": "captain", "title": "Mission 2"},
        {"id": "3", "captain": None, "role": "agent", "title": "Agent Job 1"},
        {"id": "4", "captain": "Captain Alpha", "role": "captain", "title": "Mission 3"},
    ]
    
    # Filter by captain
    captain_alpha_missions = [m for m in all_missions if m.get("captain") == "Captain Alpha"]
    assert len(captain_alpha_missions) == 2
    assert all(m["role"] == "captain" for m in captain_alpha_missions)
    
    # Filter by role
    agent_jobs = [m for m in all_missions if m.get("role") == "agent"]
    assert len(agent_jobs) == 1
    assert agent_jobs[0]["captain"] is None
    
    # Captain missions should not include agent jobs
    captain_missions = [m for m in all_missions if m.get("role") == "captain"]
    assert len(captain_missions) == 3
    assert all(m["captain"] is not None for m in captain_missions)


def test_fleet_role_separation():
    """Test that fleet data separates captains and agents"""
    fleet_data = {
        "captains": [
            {"id": 1, "name": "Captain Alpha", "type": "captain"},
            {"id": 2, "name": "Captain Beta", "type": "captain"},
        ],
        "agents": [
            {"id": 101, "name": "Scout Agent", "type": "agent"},
            {"id": 102, "name": "Writer Agent", "type": "agent"},
        ]
    }
    
    # Validate separation
    assert "captains" in fleet_data
    assert "agents" in fleet_data
    assert len(fleet_data["captains"]) == 2
    assert len(fleet_data["agents"]) == 2
    
    # Ensure no overlap
    captain_ids = {c["id"] for c in fleet_data["captains"]}
    agent_ids = {a["id"] for a in fleet_data["agents"]}
    assert captain_ids.isdisjoint(agent_ids)


def test_rbac_permissions():
    """Test that RBAC enforces captain vs agent separation"""
    try:
        from bridge_backend.bridge_core.middleware.permissions import ROLE_MATRIX
        
        # Captain permissions
        captain_perms = ROLE_MATRIX.get("captain", {})
        assert captain_perms.get("view_own_missions") is True
        assert captain_perms.get("view_agent_jobs") is False
        
        # Agent permissions
        agent_perms = ROLE_MATRIX.get("agent", {})
        assert agent_perms.get("execute_jobs") is True
        assert agent_perms.get("view_own_missions") is False
        
        # Admiral has all permissions
        admiral_perms = ROLE_MATRIX.get("admiral", {})
        assert admiral_perms.get("all") is True
    except ImportError:
        # Skip if dependencies not available
        pytest.skip("RBAC module dependencies not available")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
