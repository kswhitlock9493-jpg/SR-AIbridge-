from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add parent directory to path to allow imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from main import app
import json

client = TestClient(app)

def test_activity_from_logs(tmp_path, monkeypatch):
    vault_file = tmp_path / "events.jsonl"
    monkeypatch.setattr("bridge_backend.bridge_core.activity.routes.VAULT_LOGS_FILE", vault_file)

    # create dummy logs
    entries = [
        {"timestamp": "2025-09-27T00:00:00Z", "source": "proto", "message": "sealed SoulEcho"},
        {"timestamp": "2025-09-27T00:01:00Z", "source": "agent", "message": "adopted Vanguard"},
    ]
    vault_file.write_text("\n".join(json.dumps(e) for e in entries), encoding="utf-8")

    # call API
    r = client.get("/activity?limit=2")
    assert r.status_code == 200
    data = r.json()["activity"]
    assert len(data) == 2
    assert data[0]["action"].startswith("adopted")
    assert data[1]["action"].startswith("sealed")