from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_invoke_stub_always_returns_contract():
    r = client.post("/bridge-core/protocols/SoulEcho/invoke", json={"payload": {"ping": "pong"}})
    assert r.status_code == 200
    data = r.json()
    assert data["protocol"] == "SoulEcho"
    assert data["status"] == "ok"
    assert "state" in data
    assert "echo" in data
    assert data["echo"]["ping"] == "pong"