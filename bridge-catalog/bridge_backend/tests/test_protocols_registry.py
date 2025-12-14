from bridge_backend.bridge_core.protocols import registry

def test_register_and_list_protocols():
    registry._registry.clear()

    # register protocols
    p1 = registry.register_protocol("comms", {"version": 1})
    p2 = registry.register_protocol("ops")

    assert p1.name == "comms"
    assert p2.state == "inactive"

    # listing
    listed = registry.list_registry()
    assert any(e["name"] == "comms" for e in listed)

def test_activate_and_vault_protocol():
    registry._registry.clear()
    registry.register_protocol("nav")

    assert registry.activate_protocol("nav")
    entry = registry.get_entry("nav")
    assert entry.state == "active"

    assert registry.vault_protocol("nav")
    assert entry.state == "vaulted"

def test_missing_protocols():
    registry._registry.clear()
    assert not registry.activate_protocol("notreal")
    assert not registry.vault_protocol("notreal")
    assert registry.get_entry("notreal") is None