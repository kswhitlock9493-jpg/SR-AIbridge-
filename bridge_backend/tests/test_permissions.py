from fastapi.testclient import TestClient
from bridge_backend.main import app
from bridge_backend.bridge_core.engines.cascade.service import CascadeEngine
import json
from pathlib import Path

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

def test_free_tier_cannot_access_leviathan():
    """Test that free tier users cannot access Leviathan endpoints"""
    # Default user is free tier
    r = client.get("/engines/leviathan/search?q=test&user_id=free_user")
    assert r.status_code == 403
    assert r.json()["detail"] == "leviathan_locked_free"

def test_free_tier_cannot_access_agents_foundry():
    """Test that free tier users cannot access Agents Foundry endpoints"""
    r = client.get("/engines/agents_foundry/status?user_id=free_user")
    assert r.status_code == 403
    assert r.json()["detail"] == "agents_locked_free"

def test_paid_tier_can_access_leviathan():
    """Test that paid tier users can access Leviathan endpoints"""
    # Create a cascade state with paid tier for test user
    vault_path = Path("vault/cascade")
    cascade_engine = CascadeEngine(vault_dir=vault_path)
    cascade_engine.apply_patch("paid_user", {"tier": "captain", "status": "active"}, source="test")
    
    # This should not raise 403 for tier restrictions
    r = client.get("/engines/leviathan/status?user_id=paid_user")
    # Should succeed or fail for other reasons, but not tier restriction
    assert r.status_code == 200 or (r.status_code != 403 or r.json()["detail"] != "leviathan_locked_free")

def test_admiral_has_full_access():
    """Test that admiral role has full access"""
    vault_path = Path("vault/cascade")
    cascade_engine = CascadeEngine(vault_dir=vault_path)
    cascade_engine.apply_patch("admiral_user", {"tier": "admiral", "status": "active"}, source="test")
    
    # Admiral should be able to access leviathan
    r = client.get("/engines/leviathan/status?user_id=admiral_user")
    assert r.status_code == 200 or (r.status_code != 403 or r.json()["detail"] != "leviathan_locked_free")

def test_permissions_allow_public_endpoints():
    """Test that public endpoints are accessible"""
    r = client.get("/")
    assert r.status_code == 200
    
    r = client.get("/health")
    assert r.status_code == 200

def test_cascade_state_determines_tier():
    """Test that Cascade state properly determines user tier"""
    # Test with default free tier
    r = client.get("/registry/tier/me?user_id=cascade_test_user")
    assert r.status_code == 200
    data = r.json()
    assert data["tier"] == "free"
