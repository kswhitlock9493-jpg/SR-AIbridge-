from fastapi import APIRouter, HTTPException

try:
    from bridge_core.protocols.registry import (
        list_registry,
        get_entry,
        activate_protocol,
        vault_protocol,
        register_protocol,
    )
    from bridge_core.protocols import storage
except ImportError:
    from bridge_backend.bridge_core.protocols.registry import (
        list_registry,
        get_entry,
        activate_protocol,
        vault_protocol,
        register_protocol,
    )
    from bridge_backend.bridge_core.protocols import storage

router = APIRouter(prefix="/protocols", tags=["protocols"])

# Register some test protocols for backwards compatibility
register_protocol("comms", {"description": "handles communication protocols"})
register_protocol("ops", {"description": "operations-level routines"})  
register_protocol("nav", {"description": "navigation suite"})

@router.get("")
def list_protocols():
    """Return all registered protocols."""
    return {"protocols": list_registry()}

@router.get("/{name}")
def protocol_status(name: str):
    e = get_entry(name)
    if not e:
        raise HTTPException(status_code=404, detail="protocol_not_found")
    return {"name": e.name, "state": e.state, "details": e.details}

@router.post("/{name}/activate")
def protocol_activate(name: str):
    if not activate_protocol(name):
        raise HTTPException(status_code=404, detail="protocol_not_found")
    storage.save_registry()
    return {"name": name, "state": "active"}

@router.post("/{name}/vault")
def protocol_vault(name: str):
    if not vault_protocol(name):
        raise HTTPException(status_code=404, detail="protocol_not_found")
    storage.save_registry()
    return {"name": name, "state": "vaulted"}
