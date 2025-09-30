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