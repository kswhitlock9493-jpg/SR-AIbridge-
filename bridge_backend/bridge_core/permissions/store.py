from __future__ import annotations
from pathlib import Path
from datetime import datetime
import json
from typing import Optional
from .models import PermissionSettings

PERM_DIR = Path("vault") / "permissions"
SETTINGS_DIR = PERM_DIR / "settings"
CONSENTS_LOG = PERM_DIR / "consents.jsonl"
SETTINGS_DIR.mkdir(parents=True, exist_ok=True)
PERM_DIR.mkdir(parents=True, exist_ok=True)

def now_iso():
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"

def settings_path(captain: str) -> Path:
    return SETTINGS_DIR / f"{captain}.json"

def load_settings(captain: str) -> Optional[PermissionSettings]:
    p = settings_path(captain)
    if not p.exists():
        return None
    data = json.loads(p.read_text(encoding="utf-8"))
    return PermissionSettings(**data)

def save_settings(settings: PermissionSettings) -> None:
    p = settings_path(settings.captain)
    p.write_text(json.dumps(settings.model_dump(), indent=2), encoding="utf-8")

def append_consent_log(event: dict) -> None:
    with CONSENTS_LOG.open("a", encoding="utf-8") as f:
        event["ts"] = now_iso()
        f.write(json.dumps(event) + "\n")
