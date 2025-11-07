from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from .service import IndoctrinationEngine

router = APIRouter(prefix="/engines/indoctrination", tags=["indoctrination"])
E = IndoctrinationEngine()

class OnboardIn(BaseModel):
    name: str
    role: str
    specialties: List[str]

class CertifyIn(BaseModel):
    doctrine: str

class RevokeIn(BaseModel):
    reason: str

@router.post("/onboard")
def onboard(data: OnboardIn):
    return E.onboard(data.name, data.role, data.specialties)

@router.post("/{aid}/certify")
def certify(aid: str, data: CertifyIn):
    try:
        return E.certify(aid, data.doctrine)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/{aid}/revoke")
def revoke(aid: str, data: RevokeIn):
    try:
        return E.revoke(aid, data.reason)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/agents")
def list_agents():
    return E.list_agents()

@router.get("/status")
def get_status():
    """Get Indoctrination Engine status for deployment validation."""
    agents = E.list_agents()
    return {
        "status": "operational",
        "engine": "indoctrination",
        "version": "1.0.0",
        "agents_count": len(agents),
        "agents_certified": len([a for a in agents if a.get("certified")]),
        "vault_active": True
    }
