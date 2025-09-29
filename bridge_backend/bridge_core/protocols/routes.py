from fastapi import APIRouter
from .models import Protocol, ProtocolList

router = APIRouter(prefix="/protocols", tags=["protocols"])

# Mock in-memory data for now
PROTOCOLS = [
    {"name": "comms", "status": "available", "details": "stub"},
    {"name": "ops", "status": "available", "details": "stub"},
    {"name": "nav", "status": "available", "details": "stub"},
]


@router.get("/", response_model=ProtocolList)
def list_protocols():
    """Return a mock list of supported protocols."""
    return {"protocols": PROTOCOLS}


@router.get("/{protocol_name}", response_model=Protocol)
def get_protocol(protocol_name: str):
    """Return details for a given protocol."""
    proto = next((p for p in PROTOCOLS if p["name"] == protocol_name), None)
    if not proto:
        return Protocol(name=protocol_name, status="unknown", details="not found")
    return proto
