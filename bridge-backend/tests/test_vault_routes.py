from fastapi.testclient import TestClient
from main import app
from pathlib import Path
import json

client = TestClient(app)

def test_add_and_list_logs(tmp_path, monkeypatch):
    logs_file = tmp_path / "events.jsonl"
    monkeypatch.setattr("bridge_core.vault.routes.LOGS_FILE", logs_file)

    # Add log
    r = client.post("/vault/logs", json={"source": "unit-test", "message": "test event"})
    assert r.status_code == 200
    entry = r.json()["entry"]
    assert entry["source"] == "unit-test"
    assert entry["message"] == "test event"

    # List logs
    r = client.get("/vault/logs?limit=10")
    assert r.status_code == 200
    logs = r.json()["logs"]
    assert len(logs) >= 1
    assert logs[0]["source"] == "unit-test"