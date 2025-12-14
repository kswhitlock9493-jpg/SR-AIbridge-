from fastapi import APIRouter, HTTPException, Body, Query
from pydantic import BaseModel
from typing import Optional
from .service import Tier, get_rules
from .models import PermissionSettings
from .presets import preset_for_tier
from .store import load_settings, save_settings, append_consent_log

router = APIRouter(prefix="/permissions", tags=["permissions"])

SCHEMA = {
  "autonomy": {"enabled": "bool", "max_hours_per_day": "int", "modes": ["screen","connector","hybrid"]},
  "location": {"share": ["none","approximate","precise"]},
  "screen": {"share": "bool", "mirror": "bool", "overlay": "bool"},
  "voice": {"stt": "bool", "tts": "bool"},
  "data": {"email": "bool", "drive": "bool", "docs": "bool", "chats": "bool"},
  "logging": {"level": ["minimal","standard","verbose"], "retention_days": "int"},
  "push": {"enabled": "bool", "alerts": "bool", "updates": "bool", "reminders": "bool"},
  "consent": {"consent_version": "str", "consent_given": "bool"}
}

@router.get("/tiers")
def list_tiers():
    return {"tiers": {t.value: get_rules(t) for t in Tier}}

@router.get("/tiers/{tier_name}")
def tier_detail(tier_name: str):
    try:
        tier = Tier(tier_name)
    except ValueError:
        raise HTTPException(status_code=404, detail="tier_not_found")
    return {"tier": tier.value, "rules": get_rules(tier)}

@router.get("/schema")
def schema():
    return {"schema": SCHEMA, "version": "v1.0"}

@router.get("/current")
def current(captain: str = Query(...)):
    s = load_settings(captain)
    if not s:
        # no settings yet → default to free tier preset
        s = preset_for_tier(captain, "free")
        save_settings(s)
    return {"settings": s.model_dump()}

class UpdateIn(BaseModel):
    captain: str
    settings: PermissionSettings

@router.post("/update")
def update(payload: UpdateIn):
    if payload.captain != payload.settings.captain:
        raise HTTPException(400, "captain_mismatch")
    save_settings(payload.settings)
    append_consent_log({
        "captain": payload.captain,
        "event": "settings_update",
        "tier": payload.settings.tier,
        "settings_sha": None  # could sha256 the blob later if desired
    })
    return {"ok": True}

@router.post("/apply-tier")
def apply_tier(captain: str = Query(...), tier: str = Query(...)):
    if tier not in ("free","pro","admiral"):
        raise HTTPException(400, "invalid_tier")
    s = preset_for_tier(captain, tier)
    save_settings(s)
    append_consent_log({"captain": captain, "event": "apply_tier", "tier": tier})
    return {"ok": True, "settings": s.model_dump()}

class ConsentIn(BaseModel):
    captain: str
    accepted: bool
    version: Optional[str] = "v1.0"
    text_digest: Optional[str] = None  # optional sha256 of consent text shown

@router.post("/consent")
def consent(payload: ConsentIn):
    s = load_settings(payload.captain) or preset_for_tier(payload.captain, "free")
    s.consent_version = payload.version or "v1.0"
    s.consent_given = bool(payload.accepted)
    save_settings(s)
    append_consent_log({
        "captain": payload.captain,
        "event": "consent",
        "accepted": payload.accepted,
        "version": s.consent_version,
        "text_digest": payload.text_digest
    })
    return {"ok": True, "consented": s.consent_given}
