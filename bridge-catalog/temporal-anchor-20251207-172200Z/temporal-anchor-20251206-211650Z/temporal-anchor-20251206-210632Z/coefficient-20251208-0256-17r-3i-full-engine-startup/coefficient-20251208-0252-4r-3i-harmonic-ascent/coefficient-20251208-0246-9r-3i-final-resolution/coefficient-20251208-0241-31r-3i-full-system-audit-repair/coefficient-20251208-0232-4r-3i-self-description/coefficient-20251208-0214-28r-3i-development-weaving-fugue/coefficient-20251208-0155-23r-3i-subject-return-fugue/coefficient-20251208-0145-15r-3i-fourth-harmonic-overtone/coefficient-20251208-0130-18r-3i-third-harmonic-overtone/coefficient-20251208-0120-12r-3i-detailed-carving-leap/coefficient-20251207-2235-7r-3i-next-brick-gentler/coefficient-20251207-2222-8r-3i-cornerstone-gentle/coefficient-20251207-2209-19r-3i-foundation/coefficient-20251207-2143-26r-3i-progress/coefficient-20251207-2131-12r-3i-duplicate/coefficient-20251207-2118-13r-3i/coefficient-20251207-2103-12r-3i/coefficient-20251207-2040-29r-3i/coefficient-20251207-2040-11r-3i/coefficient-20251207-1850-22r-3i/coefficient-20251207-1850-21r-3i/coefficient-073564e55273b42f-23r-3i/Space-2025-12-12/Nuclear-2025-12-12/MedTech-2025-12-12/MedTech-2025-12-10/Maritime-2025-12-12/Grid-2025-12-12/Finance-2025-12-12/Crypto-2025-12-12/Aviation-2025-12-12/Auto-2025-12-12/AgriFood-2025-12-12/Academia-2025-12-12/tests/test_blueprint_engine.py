"""
Unit tests for Blueprint Engine
Tests the core planning logic and task generation
"""
import pytest
from bridge_backend.bridge_core.engines.blueprint.blueprint_engine import BlueprintEngine
from bridge_backend.bridge_core.engines.blueprint.planner_rules import derive_objectives, explode_tasks


def test_derive_objectives_base():
    """Test that base objectives are always included"""
    brief = "Simple project"
    objectives = derive_objectives(brief)
    
    assert len(objectives) >= 3
    assert "Clarify requirements" in objectives
    assert "Collect sources/data" in objectives
    assert "Produce deliverable" in objectives


def test_derive_objectives_marketing():
    """Test marketing-specific objectives"""
    brief = "Marketing launch for Q4"
    objectives = derive_objectives(brief)
    
    assert any("distribution" in obj.lower() for obj in objectives)


def test_derive_objectives_analysis():
    """Test analysis-specific objectives"""
    brief = "Research and analysis of market trends"
    objectives = derive_objectives(brief)
    
    assert any("analyze" in obj.lower() or "insights" in obj.lower() for obj in objectives)


def test_explode_tasks():
    """Test task explosion from objectives"""
    objectives = ["Objective 1", "Objective 2", "Objective 3"]
    brief = "Test project"
    
    tasks = explode_tasks(objectives, brief)
    
    assert len(tasks) == 3
    assert tasks[0]["key"] == "T1"
    assert tasks[1]["key"] == "T2"
    assert tasks[2]["key"] == "T3"
    
    # First task should have no dependencies
    assert tasks[0]["depends_on"] == []
    
    # Second task should depend on first
    assert tasks[1]["depends_on"] == ["T1"]
    
    # Third task should depend on second
    assert tasks[2]["depends_on"] == ["T2"]


def test_blueprint_engine_draft():
    """Test blueprint draft generation"""
    engine = BlueprintEngine()
    brief = "Marketing launch for Q4"
    
    plan = engine.draft(brief)
    
    assert "objectives" in plan
    assert "tasks" in plan
    assert "artifacts" in plan
    assert "success_criteria" in plan
    
    assert len(plan["tasks"]) >= 3
    assert len(plan["objectives"]) >= 3


def test_blueprint_engine_draft_contains_tasks():
    """Test that draft contains properly structured tasks"""
    engine = BlueprintEngine()
    brief = "Marketing launch for Q4"
    
    plan = engine.draft(brief)
    
    assert len(plan["tasks"]) >= 3
    
    # Check task structure
    for task in plan["tasks"]:
        assert "key" in task
        assert "title" in task
        assert "detail" in task
        assert "depends_on" in task
        assert "acceptance" in task


def test_agent_jobs_from_plan():
    """Test agent job generation from plan"""
    engine = BlueprintEngine()
    plan = {
        "objectives": ["Obj 1", "Obj 2"],
        "tasks": [
            {
                "key": "T1",
                "title": "Task 1",
                "detail": "Details for task 1",
                "depends_on": [],
                "role_hint": "agent",
                "acceptance": ["Criteria 1"]
            },
            {
                "key": "T2",
                "title": "Task 2",
                "detail": "Details for task 2",
                "depends_on": ["T1"],
                "role_hint": "agent",
                "acceptance": ["Criteria 2"]
            }
        ],
        "artifacts": [],
        "success_criteria": []
    }
    
    jobs = engine.agent_jobs_from_plan(
        mission_id=1,
        blueprint_id=1,
        captain="Captain-Alpha",
        plan=plan
    )
    
    assert len(jobs) == 2
    
    # Check first job
    assert jobs[0]["mission_id"] == 1
    assert jobs[0]["blueprint_id"] == 1
    assert jobs[0]["captain"] == "Captain-Alpha"
    assert jobs[0]["task_key"] == "T1"
    assert jobs[0]["status"] == "queued"
    assert jobs[0]["inputs"]["depends_on"] == []
    
    # Check second job
    assert jobs[1]["task_key"] == "T2"
    assert jobs[1]["inputs"]["depends_on"] == ["T1"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
