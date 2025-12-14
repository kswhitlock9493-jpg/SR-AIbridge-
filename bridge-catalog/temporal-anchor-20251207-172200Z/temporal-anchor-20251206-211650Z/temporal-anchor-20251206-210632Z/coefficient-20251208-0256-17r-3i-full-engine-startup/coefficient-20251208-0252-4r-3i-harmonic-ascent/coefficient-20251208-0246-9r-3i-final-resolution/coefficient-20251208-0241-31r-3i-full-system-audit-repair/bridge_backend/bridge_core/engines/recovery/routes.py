from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from .orchestrator import RecoveryOrchestrator

router = APIRouter(prefix="/engines/recovery", tags=["recovery"])
R = RecoveryOrchestrator()

class DispatchIn(BaseModel):
    project: str
    captain: str
    permissions: dict
    objective: str
    raw: str

@router.post("/dispatch-and-ingest")
def dispatch_and_ingest(payload: DispatchIn):
    try:
        return R.dispatch_and_ingest(
            project=payload.project,
            captain=payload.captain,
            permissions=payload.permissions,
            objective=payload.objective,
            raw=payload.raw
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))