from fastapi.testclient import TestClient
from bridge_backend.main import app
from pathlib import Path
import json
import importlib

client = TestClient(app)

def test_schema_and_bootstrap(tmp_path, monkeypatch):
    # redirect vault/permissions for test isolation
    perm_dir = tmp_path / "permissions"
    settings_dir = perm_dir / "settings"
    consents_log = perm_dir / "consents.jsonl"
    
    # Create directories before monkeypatching
    settings_dir.mkdir(parents=True, exist_ok=True)
    
    monkeypatch.setattr("bridge_backend.bridge_core.permissions.store.PERM_DIR", perm_dir)
    monkeypatch.setattr("bridge_backend.bridge_core.permissions.store.SETTINGS_DIR", settings_dir)
    monkeypatch.setattr("bridge_backend.bridge_core.permissions.store.CONSENTS_LOG", consents_log)
    
    # Reload to pick up the monkeypatched values
    import bridge_backend.bridge_core.permissions.store as store
    import bridge_backend.bridge_core.permissions.routes as routes
    importlib.reload(store)
    importlib.reload(routes)
    
    local = TestClient(app)

    r = local.get("/permissions/schema")
    assert r.status_code == 200
    assert r.json()["version"] == "v1.0"

    # first read creates free preset
    r = local.get("/permissions/current?captain=TestUser1")
    assert r.status_code == 200
    s = r.json()["settings"]
    assert s["tier"] == "free"
    assert s["autonomy"]["max_hours_per_day"] == 7

def test_apply_tier_update_consent(tmp_path, monkeypatch):
    perm_dir = tmp_path / "permissions"
    settings_dir = perm_dir / "settings"
    consents_log = perm_dir / "consents.jsonl"
    
    # Create directories before monkeypatching
    settings_dir.mkdir(parents=True, exist_ok=True)
    
    monkeypatch.setattr("bridge_backend.bridge_core.permissions.store.PERM_DIR", perm_dir)
    monkeypatch.setattr("bridge_backend.bridge_core.permissions.store.SETTINGS_DIR", settings_dir)
    monkeypatch.setattr("bridge_backend.bridge_core.permissions.store.CONSENTS_LOG", consents_log)
    
    # Reload to pick up the monkeypatched values
    import bridge_backend.bridge_core.permissions.store as store
    import bridge_backend.bridge_core.permissions.routes as routes
    importlib.reload(store)
    importlib.reload(routes)
    
    local = TestClient(app)

    # apply pro
    r = local.post("/permissions/apply-tier?captain=TestUser2&tier=pro")
    assert r.status_code == 200
    s = r.json()["settings"]
    assert s["tier"] == "pro"
    assert s["autonomy"]["max_hours_per_day"] == 14

    # consent
    r = local.post("/permissions/consent", json={"captain":"TestUser2","accepted":True,"version":"v1.0"})
    assert r.status_code == 200
    assert r.json()["consented"] is True

    # fetch to verify persisted
    r = local.get("/permissions/current?captain=TestUser2")
    assert r.status_code == 200
    s = r.json()["settings"]
    assert s["consent_given"] is True
