from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

VAULT_CASCADE = Path("vault") / "cascade"
VAULT_CASCADE.mkdir(parents=True, exist_ok=True)

def now_iso() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"

class CascadeEngine:
    def __init__(self, vault_dir: Path = VAULT_CASCADE):
        self.vault = vault_dir
        self.state_file = self.vault / "cascade_state.json"
        if not self.state_file.exists():
            self.state_file.write_text(json.dumps({"history": []}, indent=2))

    def apply_patch(self, captain_id: str, patch: Dict[str, Any]) -> Dict[str, Any]:
        """Apply seamless tier/engine/permission updates without downtime."""
        state = json.loads(self.state_file.read_text())
        entry = {
            "captain_id": captain_id,
            "patch": patch,
            "applied_at": now_iso()
        }
        state["history"].append(entry)
        self.state_file.write_text(json.dumps(state, indent=2))

        # Core hot-swap logic:
        # - Adjust autonomy hours
        # - Expand/contract engine access
        # - Cascade into agent registry + vault rules
        # (For now just logs, real hooks tied into middleware)
        return {"ok": True, "entry": entry}

    def history(self) -> Dict[str, Any]:
        return json.loads(self.state_file.read_text())
