"""
Tests for push notification permissions integration
"""
import pytest
import importlib
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add bridge_backend to path
bridge_backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(bridge_backend_path))

from bridge_backend.main import app


def test_push_notification_schema_in_permissions(tmp_path, monkeypatch):
    """Test that push notification settings are included in permissions schema"""
    perm_dir = tmp_path / "permissions"
    settings_dir = perm_dir / "settings"
    consents_log = perm_dir / "consents.jsonl"
    
    # Create directories
    settings_dir.mkdir(parents=True, exist_ok=True)
    
    # Monkeypatch paths
    monkeypatch.setattr("bridge_backend.bridge_core.permissions.store.PERM_DIR", perm_dir)
    monkeypatch.setattr("bridge_backend.bridge_core.permissions.store.SETTINGS_DIR", settings_dir)
    monkeypatch.setattr("bridge_backend.bridge_core.permissions.store.CONSENTS_LOG", consents_log)
    
    # Reload modules
    import bridge_backend.bridge_core.permissions.store as store
    import bridge_backend.bridge_core.permissions.routes as routes
    importlib.reload(store)
    importlib.reload(routes)
    
    client = TestClient(app)
    
    # Get schema
    r = client.get("/permissions/schema")
    assert r.status_code == 200
    schema = r.json()
    
    # Verify push is in schema
    assert "push" in schema["schema"]
    assert "enabled" in schema["schema"]["push"]
    assert "alerts" in schema["schema"]["push"]
    assert "updates" in schema["schema"]["push"]
    assert "reminders" in schema["schema"]["push"]


def test_push_permissions_in_tier_presets(tmp_path, monkeypatch):
    """Test that push permissions are set correctly in tier presets"""
    perm_dir = tmp_path / "permissions"
    settings_dir = perm_dir / "settings"
    consents_log = perm_dir / "consents.jsonl"
    
    # Create directories
    settings_dir.mkdir(parents=True, exist_ok=True)
    
    # Monkeypatch paths
    monkeypatch.setattr("bridge_backend.bridge_core.permissions.store.PERM_DIR", perm_dir)
    monkeypatch.setattr("bridge_backend.bridge_core.permissions.store.SETTINGS_DIR", settings_dir)
    monkeypatch.setattr("bridge_backend.bridge_core.permissions.store.CONSENTS_LOG", consents_log)
    
    # Reload modules
    import bridge_backend.bridge_core.permissions.store as store
    import bridge_backend.bridge_core.permissions.routes as routes
    importlib.reload(store)
    importlib.reload(routes)
    
    client = TestClient(app)
    
    # Test free tier - push should be disabled
    r = client.post("/permissions/apply-tier?captain=TestUserFree&tier=free")
    assert r.status_code == 200
    settings = r.json()["settings"]
    assert settings["push"]["enabled"] is False
    assert settings["push"]["alerts"] is False
    assert settings["push"]["updates"] is False
    assert settings["push"]["reminders"] is False
    
    # Test pro tier - push should be partially enabled
    r = client.post("/permissions/apply-tier?captain=TestUserPro&tier=pro")
    assert r.status_code == 200
    settings = r.json()["settings"]
    assert settings["push"]["enabled"] is True
    assert settings["push"]["alerts"] is True
    assert settings["push"]["updates"] is True
    assert settings["push"]["reminders"] is False
    
    # Test admiral tier - push should be fully enabled
    r = client.post("/permissions/apply-tier?captain=TestUserAdmiral&tier=admiral")
    assert r.status_code == 200
    settings = r.json()["settings"]
    assert settings["push"]["enabled"] is True
    assert settings["push"]["alerts"] is True
    assert settings["push"]["updates"] is True
    assert settings["push"]["reminders"] is True


def test_push_notification_settings_update(tmp_path, monkeypatch):
    """Test that push notification settings can be updated"""
    perm_dir = tmp_path / "permissions"
    settings_dir = perm_dir / "settings"
    consents_log = perm_dir / "consents.jsonl"
    
    # Create directories
    settings_dir.mkdir(parents=True, exist_ok=True)
    
    # Monkeypatch paths
    monkeypatch.setattr("bridge_backend.bridge_core.permissions.store.PERM_DIR", perm_dir)
    monkeypatch.setattr("bridge_backend.bridge_core.permissions.store.SETTINGS_DIR", settings_dir)
    monkeypatch.setattr("bridge_backend.bridge_core.permissions.store.CONSENTS_LOG", consents_log)
    
    # Reload modules
    import bridge_backend.bridge_core.permissions.store as store
    import bridge_backend.bridge_core.permissions.routes as routes
    importlib.reload(store)
    importlib.reload(routes)
    
    client = TestClient(app)
    
    # Get current settings (creates free tier)
    r = client.get("/permissions/current?captain=TestUserUpdate")
    assert r.status_code == 200
    settings = r.json()["settings"]
    
    # Update push settings
    settings["push"]["enabled"] = True
    settings["push"]["alerts"] = True
    
    # Save updated settings
    r = client.post("/permissions/update", json={
        "captain": "TestUserUpdate",
        "settings": settings
    })
    assert r.status_code == 200
    
    # Verify settings were saved
    r = client.get("/permissions/current?captain=TestUserUpdate")
    assert r.status_code == 200
    updated_settings = r.json()["settings"]
    assert updated_settings["push"]["enabled"] is True
    assert updated_settings["push"]["alerts"] is True
