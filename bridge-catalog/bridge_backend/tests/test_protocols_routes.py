from fastapi.testclient import TestClient
from bridge_backend.main import app

try:
    from bridge_core.protocols import storage
    from bridge_core.protocols.registry import _registry, register_protocol
except ImportError:
    from bridge_backend.bridge_core.protocols import storage
    from bridge_backend.bridge_core.protocols.registry import _registry, register_protocol

from pathlib import Path
import json
import pytest

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_registry():
    """Reset the registry before each test to ensure clean state."""
    _registry.clear()
    # Re-register test protocols with default state
    register_protocol("comms", {"description": "handles communication protocols"})
    register_protocol("ops", {"description": "operations-level routines"})
    register_protocol("nav", {"description": "navigation suite"})

def test_list_protocols():
    r = client.get("/protocols")
    assert r.status_code == 200
    data = r.json()
    assert "protocols" in data
    assert len(data["protocols"]) >= 3
    assert any(p["name"] == "comms" for p in data["protocols"])
    # Verify the protocol structure - now uses "state" instead of "status"
    comms = next(p for p in data["protocols"] if p["name"] == "comms")
    assert comms["state"] == "inactive"
    assert "description" in comms["details"]

def test_get_protocol():
    r = client.get("/protocols/comms")
    assert r.status_code == 200
    assert r.json()["name"] == "comms"
    assert r.json()["state"] == "inactive"
    assert "description" in r.json()["details"]

def test_get_nonexistent_protocol():
    r = client.get("/protocols/nonexistent")
    assert r.status_code == 404
    assert r.json()["detail"] == "protocol_not_found"

def test_activate_and_vault_protocol(tmp_path, monkeypatch):
    proto_file = tmp_path / "protocols.json"
    monkeypatch.setattr(storage, "PROTOCOLS_FILE", proto_file)

    # activate
    r = client.post("/protocols/comms/activate")
    assert r.status_code == 200
    assert r.json()["state"] == "active"

    # check persisted
    data = json.loads(proto_file.read_text(encoding="utf-8"))
    assert data["comms"]["state"] == "active"

    # vault
    r = client.post("/protocols/comms/vault")
    assert r.status_code == 200
    assert r.json()["state"] == "vaulted"

    # check persisted
    data = json.loads(proto_file.read_text(encoding="utf-8"))
    assert data["comms"]["state"] == "vaulted"