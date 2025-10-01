from __future__ import annotations
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid, json

VAULT_DIR = Path("vault") / "screen"
SESS_DIR = VAULT_DIR / "sessions"
SIG_DIR  = VAULT_DIR / "signaling"
OVER_DIR = VAULT_DIR / "overlays"
for d in (SESS_DIR, SIG_DIR, OVER_DIR): d.mkdir(parents=True, exist_ok=True)

def now_iso() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"

@dataclass
class Session:
    id: str
    mode: str               # "share" | "mirror"
    project: str
    captain: str
    permissions: Dict[str, List[str]]
    state: str              # "init" | "live" | "stopped"
    created_at: str
    updated_at: str
    meta: Dict[str, Any]

class ScreenEngine:
    def __init__(self, vault_dir: Path = VAULT_DIR):
        self.vault = vault_dir

    # ---- internal helpers ----
    def _sess_path(self, sid: str) -> Path:
        return SESS_DIR / f"{sid}.json"

    def _write(self, s: Session) -> None:
        self._sess_path(s.id).write_text(json.dumps(asdict(s), indent=2), encoding="utf-8")

    def _read(self, sid: str) -> Optional[Session]:
        p = self._sess_path(sid)
        if not p.exists(): return None
        return Session(**json.loads(p.read_text(encoding="utf-8")))

    # ---- public API ----
    def start(self, mode: str, project: str, captain: str,
              permissions: Dict[str, List[str]], meta: Optional[Dict[str, Any]] = None) -> Session:
        if mode not in ("share", "mirror"):
            raise ValueError("invalid_mode")
        sid = str(uuid.uuid4())
        ts  = now_iso()
        s = Session(
            id=sid, mode=mode, project=project, captain=captain,
            permissions=permissions or {}, state="init",
            created_at=ts, updated_at=ts, meta=meta or {}
        )
        self._write(s)
        return s

    def set_state(self, sid: str, new_state: str) -> Optional[Session]:
        s = self._read(sid)
        if not s: return None
        if new_state not in ("live", "stopped"): raise ValueError("invalid_state")
        s.state = new_state
        s.updated_at = now_iso()
        self._write(s)
        return s

    def list(self, project: Optional[str] = None, state: Optional[str] = None) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []
        for f in SESS_DIR.glob("*.json"):
            data = json.loads(f.read_text(encoding="utf-8"))
            if project and data.get("project") != project: continue
            if state and data.get("state") != state: continue
            out.append({k: data[k] for k in ("id","mode","project","captain","state","created_at","updated_at")})
        out.sort(key=lambda r: r["created_at"], reverse=True)
        return out

    def get(self, sid: str) -> Optional[Dict[str, Any]]:
        s = self._read(sid)
        return asdict(s) if s else None

    # ---- signaling stubs (store SDP/ICE; transport is BYO) ----
    def save_offer(self, sid: str, offer: Dict[str, Any]) -> Dict[str, Any]:
        (SIG_DIR / f"{sid}.offer.json").write_text(json.dumps(offer, indent=2), encoding="utf-8")
        return {"ok": True, "sid": sid, "kind": "offer"}

    def save_answer(self, sid: str, answer: Dict[str, Any]) -> Dict[str, Any]:
        (SIG_DIR / f"{sid}.answer.json").write_text(json.dumps(answer, indent=2), encoding="utf-8")
        return {"ok": True, "sid": sid, "kind": "answer"}

    def append_ice(self, sid: str, candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
        p = SIG_DIR / f"{sid}.ice.jsonl"
        with p.open("a", encoding="utf-8") as f:
            for cand in candidates:
                f.write(json.dumps(cand) + "\n")
        return {"ok": True, "sid": sid, "count": len(candidates)}

    # ---- overlay config (declarative) ----
    def apply_overlay(self, sid: str, overlay: Dict[str, Any]) -> Dict[str, Any]:
        """
        overlay = {
          "widgets": [
            {"type":"badge","text":"LIVE","x":12,"y":12},
            {"type":"highlight","rect":[x,y,w,h],"color":"#ff0","ttl":60000},
            {"type":"note","text":"Click Settings","rect":[x,y,w,h]}
          ]
        }
        """
        path = OVER_DIR / f"{sid}.{datetime.utcnow().timestamp():.0f}.json"
        path.write_text(json.dumps(overlay, indent=2), encoding="utf-8")
        return {"ok": True, "sid": sid, "path": str(path)}
