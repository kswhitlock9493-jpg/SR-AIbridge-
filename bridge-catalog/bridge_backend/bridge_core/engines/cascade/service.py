from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, Optional

VAULT_CASCADE = Path("vault") / "cascade"
VAULT_CASCADE.mkdir(parents=True, exist_ok=True)

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds") + "Z"

class CascadeEngine:
    def __init__(self, vault_dir: Path = VAULT_CASCADE):
        self.vault = vault_dir
        self.vault.mkdir(parents=True, exist_ok=True)
        self.state_file = self.vault / "cascade_state.json"
        self.patches_file = self.vault / "patches.jsonl"
        if not self.state_file.exists():
            self.state_file.write_text(json.dumps({"history": []}, indent=2))

    def apply_patch(self, captain_id: str, patch: Dict[str, Any], source: Optional[str] = None) -> Dict[str, Any]:
        """Apply seamless tier/engine/permission updates without downtime."""
        state = json.loads(self.state_file.read_text())
        timestamp = now_iso()
        entry = {
            "captain_id": captain_id,
            "patch": patch,
            "applied_at": timestamp
        }
        if source:
            entry["source"] = source
        
        state["history"].append(entry)
        self.state_file.write_text(json.dumps(state, indent=2))

        # Append to patches.jsonl for audit trail
        patch_record = {
            "captain_id": captain_id,
            "timestamp": timestamp,
            **patch
        }
        if source:
            patch_record["source"] = source
        
        with open(self.patches_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(patch_record) + "\n")

        # Core hot-swap logic:
        # - Adjust autonomy hours
        # - Expand/contract engine access
        # - Cascade into agent registry + vault rules
        # (For now just logs, real hooks tied into middleware)
        return {"ok": True, "entry": entry}

    def history(self) -> Dict[str, Any]:
        return json.loads(self.state_file.read_text())
    
    def get_state(self, captain_id: str) -> Dict[str, Any]:
        """Get the current state for a captain based on applied patches."""
        state = json.loads(self.state_file.read_text())
        history = state.get("history", [])
        
        # Find the most recent patch for this captain
        captain_patches = [entry for entry in history if entry.get("captain_id") == captain_id]
        
        if not captain_patches:
            # Return default free tier
            return {"tier": "free", "status": "active"}
        
        # Get the most recent patch
        latest_patch = captain_patches[-1]
        patch_data = latest_patch.get("patch", {})
        
        # Build current state from patch
        result = {
            "tier": patch_data.get("tier", "free"),
            "status": patch_data.get("status", "active")
        }
        
        # Include any additional fields from the patch
        for key, value in patch_data.items():
            if key not in result:
                result[key] = value
        
        return result
