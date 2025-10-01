from fastapi.testclient import TestClient
from bridge_backend.main import app
from pathlib import Path
import json
from importlib import reload

client = TestClient(app)

def test_ingest_and_list(tmp_path, monkeypatch):
    vault_dir = tmp_path / "creativity"
    ledger_file = vault_dir / "ledger.jsonl"

    monkeypatch.setattr("bridge_core.engines.creativity.service.CREATIVITY_DIR", vault_dir)
    monkeypatch.setattr("bridge_core.engines.creativity.service.LEDGER", ledger_file)

    import bridge_core.engines.creativity.service as svc
    reload(svc)
    import bridge_core.engines.creativity.routes as routes
    reload(routes)
    test_client = TestClient(app)

    # ingest
    payload = {"content": "Once upon a time in the Bridge Fleet.", "ctype": "story", "project": "mythos", "captain": "Kyle"}
    r = test_client.post("/engines/creativity/ingest", json=payload)
    assert r.status_code == 200
    sha = r.json()["sha"]

    # list
    r = test_client.get("/engines/creativity/list")
    assert r.status_code == 200
    entries = r.json()["entries"]
    assert any(e["sha"] == sha for e in entries)
