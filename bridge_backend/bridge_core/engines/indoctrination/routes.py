from fastapi import APIRouter, Depends, HTTPException
from .service import IndoctrinationEngine, AgentProfile

router = APIRouter(prefix="/indoctrination", tags=["indoctrination"])

# Lazy singleton (replace with DI container if you have one)
_engine: IndoctrinationEngine | None = None
def get_engine() -> IndoctrinationEngine:
    global _engine
    if _engine is None:
        _engine = IndoctrinationEngine()
    return _engine

@router.get("/status")
def status(engine: IndoctrinationEngine = Depends(get_engine)):
    return engine.status()

@router.get("/doctrine")
def doctrine(engine: IndoctrinationEngine = Depends(get_engine)):
    return engine.doctrine_summary()

@router.post("/indoctrinate")
def indoctrinate(agent: AgentProfile, engine: IndoctrinationEngine = Depends(get_engine)):
    rep = engine.indoctrinate(agent)
    if not rep.passed:
        # 409 makes the UI show a guard-rail rather than a hard 500
        raise HTTPException(status_code=409, detail=rep.model_dump(mode='json'))
    return rep
