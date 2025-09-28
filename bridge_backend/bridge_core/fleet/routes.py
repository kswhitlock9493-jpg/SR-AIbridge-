from fastapi import APIRouter

router = APIRouter(tags=["fleet"])

@router.get("/fleet")
def fleet_status():
    """
    Return mock fleet status.
    Later this will query DB or real orchestrator.
    """
    return {
        "ships": {
            "frigates": 3,
            "cruisers": 2,
            "dreadnoughts": 1,
        },
        "armada_ready": True,
        "total": 6,
    }

@router.get("/armada/status")
def armada_status():
    """
    Alias for /fleet, provided for frontend compatibility.
    """
    return fleet_status()