from pathlib import Path
import json
from bridge_backend.bridge_core.protocols import registry, storage

def test_save_and_load_registry(tmp_path: Path, monkeypatch):
    file = tmp_path / "protocols.json"
    monkeypatch.setattr(storage, "PROTOCOLS_FILE", file)

    # prepare registry
    registry._registry.clear()
    registry.register_protocol("comms", {"version": 1})
    registry.activate_protocol("comms")
    storage.save_registry()

    # sanity check file
    assert file.exists()
    raw = json.loads(file.read_text(encoding="utf-8"))
    assert "comms" in raw
    assert raw["comms"]["state"] == "active"

    # clear + reload
    registry._registry.clear()
    storage.load_registry()
    entry = registry.get_entry("comms")
    assert entry is not None
    assert entry.state == "active"
    assert entry.details["version"] == 1