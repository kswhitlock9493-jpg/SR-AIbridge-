from bridge_backend.bridge_core.protocols.invoke import invoke_protocol, _seal_path
from bridge_backend.bridge_core.protocols.registry import activate_protocol, vault_protocol, get_entry
import json

def test_invoke_active(tmp_path, monkeypatch):
    # redirect vault path
    monkeypatch.setattr("bridge_backend.bridge_core.protocols.invoke.VAULT_PROTOCOLS", tmp_path)

    # activate protocol
    activate_protocol("SoulEcho")
    r = invoke_protocol("SoulEcho", {"msg": "hello"})
    assert r["status"] == "invoked"
    assert r["seal"]["protocol"] == "SoulEcho"

    seal_file = _seal_path("SoulEcho")
    data = json.loads(seal_file.read_text())
    assert any(s["payload"]["msg"] == "hello" for s in data)

def test_invoke_vaulted(tmp_path, monkeypatch):
    monkeypatch.setattr("bridge_backend.bridge_core.protocols.invoke.VAULT_PROTOCOLS", tmp_path)

    # vault protocol
    vault_protocol("SoulEcho")
    r = invoke_protocol("SoulEcho", {"msg": "no-op"})
    assert r["status"] == "vaulted"

    seal_file = _seal_path("SoulEcho")
    data = json.loads(seal_file.read_text())
    assert data[-1]["state"] == "vaulted"

def test_invoke_missing_protocol(tmp_path, monkeypatch):
    monkeypatch.setattr("bridge_backend.bridge_core.protocols.invoke.VAULT_PROTOCOLS", tmp_path)

    r = invoke_protocol("NotReal", {"x": 1})
    assert "error" in r
