from fastapi.testclient import TestClient
from main import app
from pathlib import Path
import json
import uuid

client = TestClient(app)

def test_create_and_list_missions(tmp_path, monkeypatch):
    missions_file = tmp_path / "missions.jsonl"
    monkeypatch.setattr("bridge_core.missions.routes.MISSIONS_FILE", missions_file)

    # Create mission
    r = client.post("/missions", json={"title": "Test Mission", "description": "Explore sector 7"})
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "created"
    mission = data["mission"]
    assert mission["title"] == "Test Mission"
    assert "id" in mission

    # List missions
    r = client.get("/missions")
    assert r.status_code == 200
    missions = r.json()["missions"]
    assert len(missions) == 1
    assert missions[0]["title"] == "Test Mission"