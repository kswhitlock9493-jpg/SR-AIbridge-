from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_agents_list_and_status():
    r = client.get("/agents")
    assert r.status_code == 200
    assert "agents" in r.json()

    r = client.get("/agents/SoulEcho")
    assert r.status_code == 200
    assert r.json()["name"] == "SoulEcho"

def test_activate_and_vault_agent():
    r = client.post("/agents/SoulEcho/activate")
    assert r.status_code == 200
    assert r.json()["state"] == "active"

    r = client.post("/agents/SoulEcho/vault")
    assert r.status_code == 200
    assert r.json()["state"] == "vaulted"

def test_missing_agent():
    r = client.get("/agents/NotReal")
    assert r.status_code == 404