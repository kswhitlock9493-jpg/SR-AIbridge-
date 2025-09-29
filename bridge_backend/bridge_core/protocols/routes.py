from fastapi import APIRouter
from .models import Protocol, ProtocolList
from .registry import ProtocolRegistry

router = APIRouter(prefix="/protocols", tags=["protocols"])

# Instantiate registry and seed mock data
registry = ProtocolRegistry()
registry.add("comms", "available", "handles communication protocols")
registry.add("ops", "available", "operations-level routines")
registry.add("nav", "available", "navigation suite")


@router.get("/", response_model=ProtocolList)
def list_protocols():
    """Return all registered protocols."""
    return {"protocols": registry.list()}


@router.get("/{protocol_name}", response_model=Protocol)
def get_protocol(protocol_name: str):
    """Return details for a given protocol."""
    proto = registry.get(protocol_name)
    if not proto:
        return Protocol(name=protocol_name, status="unknown", details="not found")
    return proto
