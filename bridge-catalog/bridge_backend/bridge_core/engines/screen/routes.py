from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from .service import ScreenEngine

router = APIRouter(prefix="/engines/screen", tags=["screen"])
S = ScreenEngine()

class StartIn(BaseModel):
    mode: str = Field(pattern="^(share|mirror)$")
    project: str
    captain: str
    permissions: Dict[str, List[str]] = {}
    meta: Optional[Dict[str, Any]] = None

class StateIn(BaseModel):
    state: str = Field(pattern="^(live|stopped)$")

class OfferIn(BaseModel):
    sdp: Dict[str, Any]
    meta: Optional[Dict[str, Any]] = None

class AnswerIn(BaseModel):
    sdp: Dict[str, Any]

class ICEIn(BaseModel):
    candidates: List[Dict[str, Any]]

class OverlayIn(BaseModel):
    widgets: List[Dict[str, Any]]

@router.post("/start")
def start(payload: StartIn):
    s = S.start(payload.mode, payload.project, payload.captain, payload.permissions, payload.meta or {})
    return {"ok": True, "session": s.__dict__}

@router.post("/{sid}/state")
def set_state(sid: str, payload: StateIn):
    s = S.set_state(sid, payload.state)
    if not s: raise HTTPException(404, "session_not_found")
    return {"ok": True, "session": s.__dict__}

@router.get("/list")
def list_sessions(project: Optional[str] = None, state: Optional[str] = None):
    return {"sessions": S.list(project=project, state=state)}

@router.get("/{sid}")
def get_session(sid: str):
    s = S.get(sid)
    if not s: raise HTTPException(404, "session_not_found")
    return {"session": s}

# ---- signaling (placeholders) ----
@router.post("/{sid}/offer")
def save_offer(sid: str, payload: OfferIn):
    return S.save_offer(sid, {"sdp": payload.sdp, "meta": payload.meta})

@router.post("/{sid}/answer")
def save_answer(sid: str, payload: AnswerIn):
    return S.save_answer(sid, {"sdp": payload.sdp})

@router.post("/{sid}/ice")
def append_ice(sid: str, payload: ICEIn):
    return S.append_ice(sid, payload.candidates)

# ---- overlay ----
@router.post("/{sid}/overlay")
def apply_overlay(sid: str, payload: OverlayIn):
    return S.apply_overlay(sid, {"widgets": payload.widgets})
