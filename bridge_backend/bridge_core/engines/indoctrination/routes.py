from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Optional

from .service import IndoctrinationEngine

router = APIRouter(prefix="/indoctrination", tags=["indoctrination"])
_engine: Optional[IndoctrinationEngine] = None

def get_engine() -> IndoctrinationEngine:
    global _engine
    if _engine is None:
        # Optionally point to a vault file via env: INDOCTRINATION_DOCTRINE
        import os
        _engine = IndoctrinationEngine(doctrine_path=os.getenv("INDOCTRINATION_DOCTRINE"))
    return _engine

class IndoctrinateRequest(BaseModel):
    agent_id: str = Field(..., min_length=1)
    answers: Dict[str, str] = Field(default_factory=dict)

class IndoctrinateResponse(BaseModel):
    agent_id: str
    passed: bool
    score: int
    details: Dict[str, str]

@router.get("/status")
def status():
    eng = get_engine()
    return eng.status()

@router.get("/doctrine")
def doctrine():
    return get_engine().doctrine()

@router.post("/run", response_model=IndoctrinateResponse)
def run(req: IndoctrinateRequest):
    eng = get_engine()
    rec = eng.indoctrinate(req.agent_id, req.answers)
    return IndoctrinateResponse(
        agent_id=rec.agent_id, passed=rec.passed, score=rec.score, details=rec.details
    )

@router.get("/result/{agent_id}", response_model=IndoctrinateResponse)
def result(agent_id: str):
    eng = get_engine()
    rec = eng.get(agent_id)
    if not rec:
        raise HTTPException(status_code=404, detail="No record for agent")
    return IndoctrinateResponse(
        agent_id=rec.agent_id, passed=rec.passed, score=rec.score, details=rec.details
    )
