from pathlib import Path
import json, uuid
from datetime import datetime
from typing import Dict, Any, List

VAULT = Path("vault") / "indoctrination"
VAULT.mkdir(parents=True, exist_ok=True)

def now_iso():
    return datetime.utcnow().isoformat() + "Z"

class IndoctrinationEngine:
    def __init__(self, vault_dir: Path = VAULT):
        self.vault_dir = Path(vault_dir)
        self.vault_dir.mkdir(parents=True, exist_ok=True)
        self.registry: Dict[str, Dict[str, Any]] = {}

    def onboard(self, name: str, role: str, specialties: List[str]) -> Dict[str, Any]:
        aid = str(uuid.uuid4())
        rec = {
            "id": aid,
            "name": name,
            "role": role,
            "specialties": specialties,
            "status": "onboarded",
            "created_at": now_iso(),
            "certified": False,
            "certificates": [],
        }
        self.registry[aid] = rec
        self._write_vault(aid, rec)
        return rec

    def certify(self, aid: str, doctrine: str) -> Dict[str, Any]:
        agent = self.registry.get(aid)
        if not agent:
            raise ValueError("Agent not found")
        cert = {
            "doctrine": doctrine,
            "ts": now_iso(),
            "seal": str(uuid.uuid4()),
        }
        agent["certified"] = True
        agent["status"] = "certified"
        agent["certificates"].append(cert)
        self._write_vault(aid, agent)
        return cert

    def revoke(self, aid: str, reason: str) -> Dict[str, Any]:
        agent = self.registry.get(aid)
        if not agent:
            raise ValueError("Agent not found")
        agent["status"] = "revoked"
        agent["revoked_reason"] = reason
        agent["revoked_at"] = now_iso()
        self._write_vault(aid, agent)
        return agent

    def list_agents(self) -> List[Dict[str, Any]]:
        return list(self.registry.values())

    def list_scrolls(self) -> List[Dict[str, Any]]:
        """List all indoctrination scrolls (doctrine files)."""
        scrolls = []
        for scroll_file in self.vault_dir.glob("*.json"):
            try:
                data = json.loads(scroll_file.read_text(encoding="utf-8"))
                scrolls.append({
                    "id": data.get("id"),
                    "name": data.get("name"),
                    "role": data.get("role"),
                    "status": data.get("status"),
                    "created_at": data.get("created_at"),
                    "certified": data.get("certified", False),
                })
            except Exception:
                continue
        scrolls.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return scrolls

    def _write_vault(self, aid: str, rec: Dict[str, Any]):
        out = self.vault_dir / f"{aid}.json"
        out.write_text(json.dumps(rec, indent=2))
