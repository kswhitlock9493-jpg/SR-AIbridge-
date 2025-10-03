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

def test_get_my_tier():
    """Test the /registry/tier/me endpoint"""
    r = client.get("/registry/tier/me?user_id=test_captain")
    assert r.status_code == 200
    data = r.json()
    assert "tier" in data
    assert "status" in data
    assert "features" in data
    assert isinstance(data["features"], list)
    # Default should be free tier
    assert data["tier"] == "free"
    # Should have feature list
    assert len(data["features"]) > 0
    # Each feature should have label and available fields
    for feature in data["features"]:
        assert "label" in feature
        assert "available" in feature

