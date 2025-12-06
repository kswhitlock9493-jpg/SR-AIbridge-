from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Optional

router = APIRouter(prefix="/resonance", tags=["resonance"])
_engine: Optional[ResonanceAlignmentEngine] = None

def get_engine() -> ResonanceAlignmentEngine:
    global _engine
    if _engine is None:
        _engine = ResonanceAlignmentEngine(
            config_path="bridge_resonance_config.yaml",
            persistent_storage=True
        )
    return _engine

class AlignmentRequest(BaseModel):
    entity_id: str = Field(..., min_length=1)
    entity_type: str = Field(..., regex="^(human|ai|system|collective)$")
    metrics: Dict[str, float] = Field(..., description="Subsystem resonance scores 0-1")

class AlignmentResponse(BaseModel):
    entity_id: str
    resonance: float
    harmony: float
    stage: str
    laws_mastered: int
    paths_activated: int
    bridge_access: Dict[str, bool]

@router.get("/status")
def system_status():
    return get_engine().get_system_status()

@router.get("/laws")
def list_laws():
    return ResonanceAlignmentEngine.DOMINION_LAWS

@router.get("/paths")
def list_paths():
    return ResonanceAlignmentEngine.RESONANCE_PATHS

@router.post("/align", response_model=AlignmentResponse)
def align_resonance(req: AlignmentRequest):
    engine = get_engine()
    
    try:
        entity_type = EntityType(req.entity_type)
        record = engine.align_resonance(req.entity_id, entity_type, req.metrics)
        
        status = engine.get_entity_status(req.entity_id)
        
        return AlignmentResponse(
            entity_id=record.entity_id,
            resonance=record.resonance_score,
            harmony=record.harmony_coefficient,
            stage=record.alignment_stage.value,
            laws_mastered=len(record.laws_mastered),
            paths_activated=len(record.paths_activated),
            bridge_access=status["bridge_access"]
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/entity/{entity_id}")
def get_entity(entity_id: str):
    engine = get_engine()
    status = engine.get_entity_status(entity_id)
    if "error" in status:
        raise HTTPException(status_code=404, detail=status["error"])
    return status

@router.post("/heal/{entity_id}")
def trigger_healing(entity_id: str):
    engine = get_engine()
    engine.trigger_self_healing(entity_id)
    return {"message": f"Healing initiated for {entity_id}"}

@router.post("/consent/{entity_id}")
def grant_consent(entity_id: str, requester_id: str, action: str, grant: bool = True):
    engine = get_engine()
    engine.grant_consent(entity_id, requester_id, action, grant)
    return {"message": f"Consent {'granted' if grant else 'revoked'} for {action}"}
```
