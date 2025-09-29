from fastapi.testclient import TestClient
from bridge_backend.main import app

client = TestClient(app)

def test_list_protocols():
    r = client.get("/protocols/")
    assert r.status_code == 200
    data = r.json()
    assert "protocols" in data
    assert len(data["protocols"]) == 3
    assert any(p["name"] == "comms" for p in data["protocols"])
    # Verify the protocol structure
    comms = next(p for p in data["protocols"] if p["name"] == "comms")
    assert comms["status"] == "available"
    assert comms["details"] == "handles communication protocols"

def test_get_protocol():
    r = client.get("/protocols/comms")
    assert r.status_code == 200
    assert r.json()["name"] == "comms"
    assert r.json()["status"] == "available"
    assert r.json()["details"] == "handles communication protocols"

def test_get_nonexistent_protocol():
    r = client.get("/protocols/nonexistent")
    assert r.status_code == 200
    assert r.json()["name"] == "nonexistent"
    assert r.json()["status"] == "unknown"
    assert r.json()["details"] == "not found"