from fastapi.testclient import TestClient
from bridge_backend.main import app
from pathlib import Path
import shutil, json

client = TestClient(app)

def test_registry_list_and_project(monkeypatch, tmp_path):
    # patch vault dirs for clean isolation
    agents_dir = tmp_path / "agents"
    indo_dir = tmp_path / "indo"
    monkeypatch.setattr("bridge_backend.bridge_core.registry.agents_registry.VAULT_ROOT", tmp_path)

    # reload registry with patched dirs
    from importlib import reload
    import bridge_backend.bridge_core.registry.agents_registry as reg
    reload(reg)
    R = reg.AgentRegistry(indo_dir, agents_dir)

    # ensure empty at start
    data = R.list_all()
    assert data["count"]["agents"] == 0
    assert data["count"]["scrolls"] == 0

def test_registry_routes(monkeypatch, tmp_path):
    agents_dir = tmp_path / "agents"
    indo_dir = tmp_path / "indo"
    monkeypatch.setattr("bridge_backend.bridge_core.registry.agents_registry.VAULT_ROOT", tmp_path)

    from importlib import reload
    import bridge_backend.bridge_core.registry.routes as routes
    reload(routes)
    test_client = TestClient(app)

    r = test_client.get("/registry/agents/all")
    assert r.status_code == 200
    assert "agents" in r.json()
