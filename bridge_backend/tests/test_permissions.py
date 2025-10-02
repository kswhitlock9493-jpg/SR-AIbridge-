from fastapi.testclient import TestClient
from bridge_backend.main import app

client = TestClient(app)

def test_list_tiers():
    r = client.get("/permissions/tiers")
    assert r.status_code == 200
    data = r.json()
    assert "tiers" in data
    assert "free" in data["tiers"]
    assert data["tiers"]["free"]["autonomy_hours"] == 2

def test_tier_detail():
    r = client.get("/permissions/tiers/captain")
    assert r.status_code == 200
    data = r.json()
    assert data["tier"] == "captain"
    assert "leviathan" in data["rules"]["features"]

def test_missing_tier():
    r = client.get("/permissions/tiers/ghost")
    assert r.status_code == 404
