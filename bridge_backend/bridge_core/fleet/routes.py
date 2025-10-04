from fastapi import APIRouter, Query

router = APIRouter(tags=["fleet"])

@router.get("/fleet")
def fleet_status(
    role: str = Query(None, description="Filter by role: 'captain' or 'agent'")
):
    """
    Return mock fleet status, filterable by role.
    Later this will query DB or real orchestrator.
    """
    # Mock data - in production this would come from database
    all_ships = {
        "captains": [
            {"id": 1, "name": "Captain Alpha", "type": "captain", "status": "active", "ships": 2},
            {"id": 2, "name": "Captain Beta", "type": "captain", "status": "active", "ships": 1},
            {"id": 3, "name": "Captain Gamma", "type": "captain", "status": "standby", "ships": 1},
        ],
        "agents": [
            {"id": 101, "name": "Scout Agent Alpha", "type": "agent", "status": "active", "location": "Sector 7"},
            {"id": 102, "name": "Writer Agent Beta", "type": "agent", "status": "active", "location": "Portal"},
            {"id": 103, "name": "Automation Agent", "type": "agent", "status": "active", "location": "Backend"},
        ],
    }
    
    if role == "captain":
        return {"ships": all_ships["captains"], "total": len(all_ships["captains"])}
    elif role == "agent":
        return {"ships": all_ships["agents"], "total": len(all_ships["agents"])}
    else:
        # Return both with role distinction
        return {
            "ships": {
                "frigates": 3,
                "cruisers": 2,
                "dreadnoughts": 1,
            },
            "captains": all_ships["captains"],
            "agents": all_ships["agents"],
            "armada_ready": True,
            "total": 6,
        }

@router.get("/armada/status")
def armada_status(
    role: str = Query(None, description="Filter by role: 'captain' or 'agent'")
):
    """
    Alias for /fleet, provided for frontend compatibility.
    """
    return fleet_status(role)