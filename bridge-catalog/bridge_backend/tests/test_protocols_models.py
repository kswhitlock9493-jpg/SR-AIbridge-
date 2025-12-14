from bridge_core.protocols.models import Protocol, ProtocolList

def test_protocol_model():
    proto = Protocol(name="comms", status="available", details="stub")
    assert proto.name == "comms"
    assert proto.status == "available"
    assert proto.details == "stub"

def test_protocol_list_model():
    lst = ProtocolList(protocols=[{"name": "ops", "status": "available"}])
    assert lst.protocols[0].name == "ops"