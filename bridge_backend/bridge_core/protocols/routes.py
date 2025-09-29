from fastapi import APIRouter

router = APIRouter(prefix="/protocols", tags=["protocols"])

@router.get("/")
def list_protocols():
    """Return a mock list of supported protocols."""
    return {
        "protocols": [
            {"name": "comms", "status": "available"},
            {"name": "ops", "status": "available"},
            {"name": "nav", "status": "available"},
        ]
    }

@router.get("/{protocol_name}")
def get_protocol(protocol_name: str):
    """Stub: return details for a given protocol."""
    return {"protocol": protocol_name, "details": "stub"}
