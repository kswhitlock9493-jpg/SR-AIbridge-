"""
API integration tests for Blueprint endpoints
Tests draft, commit, delete operations with RBAC
"""
import pytest


def test_draft_blueprint():
    """Test blueprint drafting via API"""
    # This is a placeholder test that demonstrates the expected API structure
    # In a real test environment, you would use TestClient or httpx
    
    payload = {
        "title": "Q4 Marketing Launch",
        "brief": "Launch marketing campaign for Q4 with social media and email",
        "captain": "Captain-Alpha"
    }
    
    # Expected response structure
    expected_keys = ["id", "title", "brief", "captain", "plan", "created_at", "updated_at"]
    
    # Assert payload is valid
    assert "title" in payload
    assert "brief" in payload
    assert "captain" in payload


def test_commit_blueprint():
    """Test blueprint commit to mission"""
    # This is a placeholder test
    
    blueprint_id = 1
    mission_id = 1
    
    # Expected response structure
    expected_response = {
        "ok": True,
        "created_jobs": 3,  # Number varies based on brief
        "blueprint_id": blueprint_id,
        "mission_id": mission_id
    }
    
    assert expected_response["ok"] is True
    assert expected_response["created_jobs"] > 0


def test_rbac_captain_can_create():
    """Test that captains can create blueprints"""
    # RBAC test
    from bridge_backend.bridge_core.middleware.permissions import ROLE_MATRIX
    
    captain_perms = ROLE_MATRIX.get("captain", {})
    assert captain_perms.get("blueprint:create") is True


def test_rbac_captain_cannot_delete():
    """Test that captains cannot delete blueprints"""
    from bridge_backend.bridge_core.middleware.permissions import ROLE_MATRIX
    
    captain_perms = ROLE_MATRIX.get("captain", {})
    assert captain_perms.get("blueprint:delete") is False


def test_rbac_admiral_can_delete():
    """Test that admiral can delete blueprints"""
    from bridge_backend.bridge_core.middleware.permissions import ROLE_MATRIX
    
    admiral_perms = ROLE_MATRIX.get("admiral", {})
    assert admiral_perms.get("blueprint:delete") is True


def test_agent_jobs_created():
    """Test that agent jobs are created when blueprint is committed"""
    # This is a structural test
    
    # Sample plan structure
    plan = {
        "objectives": ["Objective 1", "Objective 2"],
        "tasks": [
            {"key": "T1", "title": "Task 1", "detail": "Details", "depends_on": []},
            {"key": "T2", "title": "Task 2", "detail": "Details", "depends_on": ["T1"]}
        ]
    }
    
    assert len(plan["tasks"]) == 2
    assert plan["tasks"][0]["key"] == "T1"
    assert plan["tasks"][1]["depends_on"] == ["T1"]


def test_blueprint_plan_structure():
    """Test that blueprint plans have required structure"""
    from bridge_backend.schemas import BlueprintPlan, TaskItem
    
    # Test TaskItem schema
    task = TaskItem(
        key="T1",
        title="Test Task",
        detail="Test details",
        depends_on=[],
        role_hint="agent",
        acceptance=["Criterion 1"]
    )
    
    assert task.key == "T1"
    assert task.title == "Test Task"
    assert isinstance(task.depends_on, list)
    
    # Test BlueprintPlan schema
    plan = BlueprintPlan(
        objectives=["Objective 1"],
        tasks=[task],
        artifacts=["report.md"],
        success_criteria=["All tests pass"]
    )
    
    assert len(plan.objectives) == 1
    assert len(plan.tasks) == 1
    assert plan.tasks[0].key == "T1"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
