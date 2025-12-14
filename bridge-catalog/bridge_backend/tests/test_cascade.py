from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_apply_patch_and_history(tmp_path, monkeypatch):
    from bridge_core.engines.cascade import service
    monkeypatch.setattr(service, "VAULT_CASCADE", tmp_path)
    C = service.CascadeEngine(tmp_path)

    r = client.post("/engines/cascade/apply?captain_id=kyle", json={"tier":"paid"})
    assert r.status_code == 200
    data = r.json()["entry"]
    assert data["captain_id"] == "kyle"

    r = client.get("/engines/cascade/history")
    assert r.status_code == 200
    assert len(r.json()["history"]) > 0
