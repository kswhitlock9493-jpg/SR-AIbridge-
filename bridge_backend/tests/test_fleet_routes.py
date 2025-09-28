from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_fleet_status():
    r = client.get("/fleet")
    assert r.status_code == 200
    data = r.json()
    assert "ships" in data
    assert "total" in data
    assert data["total"] == sum(data["ships"].values())

def test_armada_status_alias():
    r = client.get("/armada/status")
    assert r.status_code == 200
    data = r.json()
    assert "ships" in data
    assert data["armada_ready"] is True