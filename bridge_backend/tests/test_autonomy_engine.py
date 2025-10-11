from fastapi.testclient import TestClient
from bridge_backend.main import app

client = TestClient(app)

def test_create_and_update_task():
    r = client.post("/engines/autonomy/task", json={
        "project": "research",
        "captain": "Kyle",
        "objective": "recover_drive_notes",
        "permissions": {"read": ["docs", "email"]},
        "mode": "screen"
    })
    assert r.status_code == 200
    tid = r.json()["task"]["id"]

    u = client.post(f"/engines/autonomy/task/{tid}/status",
                    json={"status":"complete","result":{"count":5}})
    assert u.status_code == 200
    assert u.json()["task"]["status"] == "complete"

def test_different_modes():
    """Test creating tasks with different modes"""
    modes = ["screen", "connector", "hybrid"]
    
    for mode in modes:
        r = client.post("/engines/autonomy/task", json={
            "project": "test_project",
            "captain": "TestCaptain",
            "objective": f"test_objective_{mode}",
            "permissions": {"execute": ["test"]},
            "mode": mode
        })
        assert r.status_code == 200
        task = r.json()["task"]
        assert task["mode"] == mode
        assert task["project"] == "test_project"
        assert task["status"] == "pending"

def test_list_tasks():
    """Test listing tasks"""
    # Create a task first
    r = client.post("/engines/autonomy/task", json={
        "project": "list_test",
        "captain": "ListCaptain",
        "objective": "test_listing",
        "permissions": {"read": ["vault"]},
        "mode": "screen"
    })
    assert r.status_code == 200
    
    # List tasks
    r = client.get("/engines/autonomy/tasks")
    assert r.status_code == 200
    tasks = r.json()["tasks"]
    assert len(tasks) > 0
    
    # Find our task
    test_task = next((t for t in tasks if t["project"] == "list_test"), None)
    assert test_task is not None
    assert test_task["captain"] == "ListCaptain"

def test_update_nonexistent_task():
    """Test updating a non-existent task returns 404"""
    r = client.post("/engines/autonomy/task/fake-id/status",
                    json={"status": "failed"})
    assert r.status_code == 404
    assert r.json()["detail"] == "task_not_found"

def test_task_with_originality_check():
    """Test task creation with originality verification enabled"""
    r = client.post("/engines/autonomy/task", json={
        "project": "autonomy",
        "captain": "OriginCaptain",
        "objective": "test_originality_check",
        "permissions": {"read": ["vault"]},
        "mode": "screen",
        "verify_originality": True
    })
    assert r.status_code == 200
    task = r.json()["task"]
    
    # Check that compliance check was performed
    assert "compliance_check" in task
    assert task["compliance_check"] is not None
    
    # Check that LOC metrics were collected
    assert "loc_metrics" in task
    assert task["loc_metrics"] is not None
    
    # Check originality_verified flag
    assert "originality_verified" in task
    assert isinstance(task["originality_verified"], bool)

def test_task_without_originality_check():
    """Test task creation with originality verification disabled"""
    r = client.post("/engines/autonomy/task", json={
        "project": "test_project",
        "captain": "NoCheckCaptain",
        "objective": "test_without_check",
        "permissions": {"write": ["logs"]},
        "mode": "connector",
        "verify_originality": False
    })
    assert r.status_code == 200
    task = r.json()["task"]
    
    # Compliance check should be None when disabled
    assert task["compliance_check"] is None
    
    # LOC metrics should still be collected
    assert "loc_metrics" in task
    
    # Originality should not be verified
    assert task["originality_verified"] is False

def test_task_compliance_and_loc_metrics():
    """Test that compliance check and LOC metrics have expected structure"""
    r = client.post("/engines/autonomy/task", json={
        "project": "autonomy",
        "captain": "MetricsCaptain",
        "objective": "test_metrics_structure",
        "permissions": {"execute": ["engines"]},
        "mode": "screen",
        "verify_originality": True
    })
    assert r.status_code == 200
    task = r.json()["task"]
    
    # Verify compliance check structure
    if task["compliance_check"] is not None:
        compliance = task["compliance_check"]
        assert "state" in compliance
        assert compliance["state"] in ["ok", "flagged", "blocked", "error"]
        assert "timestamp" in compliance
        
        if compliance["state"] != "error":
            assert "license" in compliance
            assert "counterfeit" in compliance
    
    # Verify LOC metrics structure
    if task["loc_metrics"] is not None:
        loc = task["loc_metrics"]
        assert "timestamp" in loc
        
        if "error" not in loc:
            assert "total_lines" in loc
            assert "total_files" in loc
            assert "by_type" in loc
            assert isinstance(loc["total_lines"], int)
            assert isinstance(loc["total_files"], int)