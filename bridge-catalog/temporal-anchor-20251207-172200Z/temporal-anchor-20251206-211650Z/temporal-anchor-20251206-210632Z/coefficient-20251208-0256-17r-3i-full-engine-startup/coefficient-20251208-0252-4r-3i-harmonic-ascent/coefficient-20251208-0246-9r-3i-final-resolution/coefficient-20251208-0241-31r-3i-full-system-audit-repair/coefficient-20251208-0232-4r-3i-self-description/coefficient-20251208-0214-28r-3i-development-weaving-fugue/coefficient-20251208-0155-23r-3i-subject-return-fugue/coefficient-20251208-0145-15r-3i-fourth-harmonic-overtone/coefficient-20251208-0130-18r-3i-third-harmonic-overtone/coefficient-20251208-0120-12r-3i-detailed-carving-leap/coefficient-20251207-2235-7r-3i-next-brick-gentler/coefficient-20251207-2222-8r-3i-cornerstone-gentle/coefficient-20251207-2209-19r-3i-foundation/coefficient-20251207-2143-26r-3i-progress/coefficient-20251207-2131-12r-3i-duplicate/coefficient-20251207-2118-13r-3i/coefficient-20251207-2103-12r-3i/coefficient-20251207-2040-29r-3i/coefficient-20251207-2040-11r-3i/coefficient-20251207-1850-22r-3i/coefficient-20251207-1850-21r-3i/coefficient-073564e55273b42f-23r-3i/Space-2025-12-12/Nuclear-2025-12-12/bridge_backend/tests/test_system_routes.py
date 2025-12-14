from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_and_status():
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data

    r = client.get("/status")
    assert r.status_code == 200
    data = r.json()
    assert "components" in data
    assert "database" in data["components"]
    assert "vault" in data["components"]