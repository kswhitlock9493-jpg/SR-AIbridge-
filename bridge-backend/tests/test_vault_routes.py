from fastapi.testclient import TestClient
from main import app
from pathlib import Path
import json
import tempfile

client = TestClient(app)

def test_vault_add_and_list(monkeypatch, tmp_path: Path):
    vault_file = tmp_path / "events.jsonl"
    monkeypatch.setattr("bridge_core.vault.routes.VAULT_LOGS_FILE", vault_file)

    # add log
    r = client.post("/vault/logs", json={"source": "test", "message": "seal event"})
    assert r.status_code == 200
    entry = r.json()["entry"]
    assert entry["source"] == "test"

    # list logs
    r = client.get("/vault/logs")
    assert r.status_code == 200
    logs = r.json()["logs"]
    assert any(log["message"] == "seal event" for log in logs)