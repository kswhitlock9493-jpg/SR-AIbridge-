from fastapi.testclient import TestClient
from bridge_backend.main import app
from pathlib import Path
import json
import shutil

client = TestClient(app)

def test_create_list_get_activate_retire(tmp_path, monkeypatch):
    vault_agents = tmp_path / "agents"
    # re-point the foundry to temp vault
    monkeypatch.setattr("bridge_backend.bridge_core.engines.agents_foundry.service.AGENTS_DIR", vault_agents)
    # reimport service to rebind default instance in routes
    from importlib import reload
    import bridge_backend.bridge_core.engines.agents_foundry.service as svc
    reload(svc)
    import bridge_backend.bridge_core.engines.agents_foundry.routes as routes
    reload(routes)
    test_client = TestClient(app)

    # templates
    r = test_client.get("/engines/agents/templates")
    assert r.status_code == 200
    assert "jarvis" in r.json()["archetypes"]

    # create
    payload = {
        "name": "Poe",
        "archetype": "poe",
        "role": "strategist",
        "project": "nova",
        "captain": "Kyle",
        "permissions": {"read": ["docs"], "write": ["notes"]},
        "tone": "literary"
    }
    r = test_client.post("/engines/agents/create", json=payload)
    assert r.status_code == 200
    mid = r.json()["manifest"]["id"]

    # list
    r = test_client.get("/engines/agents/list?project=nova")
    assert r.status_code == 200
    assert any(a["id"] == mid for a in r.json()["agents"])

    # get
    r = test_client.get(f"/engines/agents/{mid}")
    assert r.status_code == 200
    m = r.json()["manifest"]
    assert m["name"] == "Poe"
    assert m["persona"]["archetype"] == "poe"

    # activate
    r = test_client.post(f"/engines/agents/{mid}/activate")
    assert r.status_code == 200
    assert r.json()["state"] == "active"

    # retire
    r = test_client.post(f"/engines/agents/{mid}/retire")
    assert r.status_code == 200
    assert r.json()["state"] == "retired"
