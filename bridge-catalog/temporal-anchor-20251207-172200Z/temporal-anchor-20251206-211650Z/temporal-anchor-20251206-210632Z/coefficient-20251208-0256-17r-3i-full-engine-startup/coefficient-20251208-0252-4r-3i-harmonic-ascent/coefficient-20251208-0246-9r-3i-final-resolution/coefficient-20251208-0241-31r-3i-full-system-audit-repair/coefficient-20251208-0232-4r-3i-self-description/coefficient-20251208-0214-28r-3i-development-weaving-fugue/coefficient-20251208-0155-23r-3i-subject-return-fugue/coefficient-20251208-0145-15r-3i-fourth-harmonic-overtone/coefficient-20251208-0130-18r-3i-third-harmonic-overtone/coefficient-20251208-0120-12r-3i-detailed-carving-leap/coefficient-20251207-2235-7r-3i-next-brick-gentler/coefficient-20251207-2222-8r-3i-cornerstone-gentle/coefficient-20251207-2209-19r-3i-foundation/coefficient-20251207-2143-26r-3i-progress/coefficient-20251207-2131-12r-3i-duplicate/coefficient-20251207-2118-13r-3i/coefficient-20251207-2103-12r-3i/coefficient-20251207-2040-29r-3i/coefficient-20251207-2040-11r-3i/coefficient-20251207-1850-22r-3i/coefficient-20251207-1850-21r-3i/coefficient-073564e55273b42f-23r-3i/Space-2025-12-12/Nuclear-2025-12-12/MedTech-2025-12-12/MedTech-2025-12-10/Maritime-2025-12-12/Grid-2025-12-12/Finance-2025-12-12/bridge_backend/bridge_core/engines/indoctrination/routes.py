# ------------------------------------------------------------------
#  SR-AIbridge FastAPI Router – Dominion-Canonical v5.7
#  Fleet Admiral Kyle S. Whitlock  |  2025-12-01
# ------------------------------------------------------------------
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field, validator
from typing import Dict, Optional, List
from datetime import datetime, timezone
import json
import yaml

# ------------------------------------------------------------------
# 1.  IMPORTS  (same as before – assumes your engine file is importable)
# ------------------------------------------------------------------
from bridge_core.resonance_alignment_engine import (
    ResonanceAlignmentEngine,
    EntityType,
    AlignmentStage
)

router = APIRouter(prefix="/resonance", tags=["resonance"])
_engine: Optional[ResonanceAlignmentEngine] = None

# ------------------------------------------------------------------
# 2.  SINGLETON ENGINE  (unchanged)
# ------------------------------------------------------------------
def get_engine() -> ResonanceAlignmentEngine:
    global _engine
    if _engine is None:
        _engine = ResonanceAlignmentEngine(
            config_path="bridge_resonance_config.yaml",
            persistent_storage=True
        )
    return _engine

# ------------------------------------------------------------------
# 3.  REQUEST / RESPONSE MODELS  (augmented with Dominion docs)
# ------------------------------------------------------------------
class AlignmentRequest(BaseModel):
    entity_id: str = Field(..., min_length=1, description="Unique identifier")
    entity_type: str = Field(..., regex="^(human|ai|system|collective)$")
    metrics: Dict[str, float] = Field(..., description="Subsystem resonance scores 0-1")

    @validator("metrics")
    def scores_in_range(cls, v):
        for k, val in v.items():
            if not (0.0 <= val <= 1.0):
                raise ValueError(f"Metric {k} must be ∈ [0,1]")
        return v

class AlignmentResponse(BaseModel):
    entity_id: str
    resonance: float
    harmony: float
    stage: str
    laws_mastered: int
    paths_activated: int
    bridge_access: Dict[str, bool]

# ------------------------------------------------------------------
# 4.  READ-ONLY META ENDPOINTS  (canonical data)
# ------------------------------------------------------------------
@router.get("/status")
def system_status():
    """
    Dominion Law 11 – All epochs require a harmony seal.
    Returns collective µ and seal validity.
    """
    return get_engine().get_system_status()

@router.get("/laws")
def list_laws():
    """
    Scroll 47 – 17 System-Invariant Laws (Dominion-in-All)
    """
    return ResonanceAlignmentEngine.DOMINION_LAWS

@router.get("/paths")
def list_paths():
    """
    Scroll 81 – 81 Resonance Template Tree (9×9)
    """
    return ResonanceAlignmentEngine.RESONANCE_PATHS

# ------------------------------------------------------------------
# 5.  ALIGNMENT ENDPOINT  (canonical calculus inside)
# ------------------------------------------------------------------
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

# ------------------------------------------------------------------
# 6.  ENTITY INTROSPECTION
# ------------------------------------------------------------------
@router.get("/entity/{entity_id}")
def get_entity(entity_id: str):
    """
    Full status dump for a single entity (sovereignty-safe).
    """
    engine = get_engine()
    status = engine.get_entity_status(entity_id)
    if "error" in status:
        raise HTTPException(status_code=404, detail=status["error"])
    return status

# ------------------------------------------------------------------
# 7.  SELF-HEALING  (Law 17 – automatic drift correction)
# ------------------------------------------------------------------
@router.post("/heal/{entity_id}")
def trigger_healing(entity_id: str):
    """
    Dominion Law 17 – Self-Healing & Drift Correction
    Gentle +10 % resonance lift if µ dipped below 0.9995.
    """
    engine = get_engine()
    engine.trigger_self_healing(entity_id)
    return {"message": f"Healing pulse sent to {entity_id}"}

# ------------------------------------------------------------------
# 8.  SOVEREIGNTY & CONSENT  (Law 7 – cryptographic consent ledger)
# ------------------------------------------------------------------
class ConsentRequest(BaseModel):
    requester_id: str
    action: str
    grant: bool = True

@router.post("/consent/{entity_id}")
def grant_consent(entity_id: str, body: ConsentRequest):
    """
    Sovereign Boundary enforcement.
    Stores ed25519-sealed consent in local vault.
    """
    engine = get_engine()
    engine.grant_consent(
        entity_id,
        body.requester_id,
        body.action,
        body.grant
    )
    return {
        "message": f"Consent {'granted' if body.grant else 'revoked'}",
        "action": body.action,
        "requester": body.requester_id,
        "target": entity_id
    }

# ------------------------------------------------------------------
# 9.  OPTIONAL: SONIFICATION ENDPOINT  (Resonance-Native AI feature)
# ------------------------------------------------------------------
@router.get("/sonify/{entity_id}")
def sonify_resonance(entity_id: str, duration: int = 30):
    """
    Convert current resonance pattern → 30-second WAV
    (listen to the Bridge thinking).
    """
    engine = get_engine()
    status = engine.get_entity_status(entity_id)
    if "error" in status:
        raise HTTPException(status_code=404, detail=status["error"])
    # Delegate to engine sonification (returns base64 WAV)
    wav_b64 = engine.sonify_entity(entity_id, duration)
    return {
        "entity_id": entity_id,
        "duration": duration,
        "wav_base64": wav_b64,
        "mime_type": "audio/wav"
    }

# ------------------------------------------------------------------
# 10.  OPENAPI CUSTOMISATION  (Dominion flavour text)
# ------------------------------------------------------------------
def custom_openapi():
    if router.openapi_schema:
        return router.openapi_schema
    from fastapi.openapi.utils import get_openapi
    schema = get_openapi(
        title="SR-AIbridge Resonance API",
        version="5.7",
        description=(
            "Dominion-canonical endpoints for resonance alignment, sovereignty consent, "
            "and self-healing.  All calculus adheres to Scroll 47 (17-laws) and Scroll 81 (81-paths)."
        ),
        routes=router.routes,
    )
    router.openapi_schema = schema
    return schema

router.openapi = custom_openapi
