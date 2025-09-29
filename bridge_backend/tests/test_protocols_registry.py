from bridge_backend.bridge_core.protocols.registry import ProtocolRegistry


def test_protocol_registry_add_and_get():
    reg = ProtocolRegistry()
    reg.add("test", "available", "testing")
    p = reg.get("test")
    assert p is not None
    assert p["name"] == "test"
    assert p["status"] == "available"


def test_protocol_registry_list_and_clear():
    reg = ProtocolRegistry()
    reg.add("a", "available")
    reg.add("b", "standby")
    lst = reg.list()
    assert len(lst) == 2
    reg.clear()
    assert reg.list() == []