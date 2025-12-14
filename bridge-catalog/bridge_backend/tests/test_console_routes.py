from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_console_snapshot_and_summary():
    r = client.get("/console/snapshot")
    assert r.status_code == 200
    data = r.json()
    assert "protocols" in data
    assert "guardians" in data
    assert data["status"] == "ok"

    r = client.get("/console/summary")
    assert r.status_code == 200
    summary = r.json()
    assert "protocols_total" in summary
    assert "guardians_total" in summary
    assert summary["status"] == "ok"