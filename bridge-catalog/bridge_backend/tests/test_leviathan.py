from fastapi.testclient import TestClient
from bridge_backend.main import app
import shutil
from pathlib import Path

client = TestClient(app)

def test_index_and_search(tmp_path, monkeypatch):
    db_file = tmp_path / "index.db"
    ledger_file = tmp_path / "ledger.jsonl"
    levi_dir = tmp_path
    monkeypatch.setattr("bridge_backend.bridge_core.engines.leviathan.service.LEVIATHAN_DIR", levi_dir)
    monkeypatch.setattr("bridge_backend.bridge_core.engines.leviathan.service.DB", db_file)
    monkeypatch.setattr("bridge_backend.bridge_core.engines.leviathan.service.LEDGER", ledger_file)
    
    from bridge_backend.bridge_core.engines.leviathan.service import LeviathanEngine
    L = LeviathanEngine()
    monkeypatch.setattr("bridge_backend.bridge_core.engines.leviathan.routes.L", L)

    # index
    r = client.post("/engines/leviathan/index", json={
        "text": "Project Nova phase two is active.",
        "namespace": "parser",
        "source": "docs/nova.txt"
    })
    assert r.status_code == 200
    sha = r.json()["sha"]

    # search
    r = client.post("/engines/leviathan/search", json={
        "query": "Nova", "namespaces": ["parser"], "limit": 10
    })
    assert r.status_code == 200
    data = r.json()["results"]
    assert any("Nova" in d["text"] for d in data)

    # sources
    r = client.get("/engines/leviathan/sources")
    assert r.status_code == 200
    assert "parser" in r.json()["sources"]

    # web stub
    r = client.get("/engines/leviathan/web", params={"q": "test"})
    assert r.status_code == 200
    assert r.json()["query"] == "test"
