from fastapi.testclient import TestClient
from bridge_backend.main import app

client = TestClient(app)

def test_list_protocols():
    r = client.get("/protocols/")
    assert r.status_code == 200
    data = r.json()
    assert "protocols" in data
    assert any(p["name"] == "comms" for p in data["protocols"])

def test_get_protocol():
    r = client.get("/protocols/comms")
    assert r.status_code == 200
    assert r.json()["protocol"] == "comms"