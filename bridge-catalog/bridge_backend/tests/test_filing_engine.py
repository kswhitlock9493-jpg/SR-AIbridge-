from fastapi.testclient import TestClient
from bridge_backend.main import app

client = TestClient(app)

def test_file_and_search_and_reassemble(tmp_path, monkeypatch):
    monkeypatch.setattr("bridge_backend.bridge_core.engines.filing.VAULT_DIR", str(tmp_path))
    monkeypatch.setattr("bridge_backend.bridge_core.engines.filing.LEDGER_PATH", str(tmp_path / "ledger.jsonl"))

    # File content
    r = client.post("/engines/filing/file", json={
        "content": "Hello Filing World",
        "tags": ["test"],
        "source": "unit"
    })
    assert r.status_code == 200
    sha = r.json()["sha"]

    # Search by tag
    r = client.post("/engines/filing/search", json={"tag": "test"})
    assert r.status_code == 200
    assert any(entry["sha"] == sha for entry in r.json()["results"])

    # Reassemble
    r = client.post("/engines/filing/reassemble", json={"shas": [sha]})
    assert r.status_code == 200
    assert "Hello Filing World" in r.json()["text"]