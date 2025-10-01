from __future__ import annotations
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
import json, uuid, hashlib

from bridge_core.engines.leviathan.service import LeviathanEngine

VAULT = Path("vault")
CREATIVITY_DIR = VAULT / "creativity"
CREATIVITY_DIR.mkdir(parents=True, exist_ok=True)
LEDGER = CREATIVITY_DIR / "ledger.jsonl"

def now_iso() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"

def sha256_text(t: str) -> str:
    return hashlib.sha256(t.encode("utf-8", "ignore")).hexdigest()

class CreativityBay:
    def __init__(self, vault_dir: Path = CREATIVITY_DIR):
        self.vault = vault_dir
        self.vault.mkdir(parents=True, exist_ok=True)
        self.leviathan = LeviathanEngine()

    def ingest(self, content: str, ctype: str, project: Optional[str] = None,
               captain: Optional[str] = None, tags: Optional[List[str]] = None) -> Dict[str, Any]:
        sha = sha256_text(content)
        ts = now_iso()
        entry = {
            "id": str(uuid.uuid4()),
            "sha": sha,
            "type": ctype,
            "project": project,
            "captain": captain,
            "tags": tags or [],
            "ts": ts,
        }
        # write content to vault file
        f = self.vault / f"{sha}.txt"
        f.write_text(content, encoding="utf-8")

        # append to ledger
        with LEDGER.open("a", encoding="utf-8") as log:
            log.write(json.dumps(entry) + "\n")

        # index into leviathan
        self.leviathan.index(content, namespace=f"creativity:{ctype}", source=f"vault/creativity/{sha}.txt")

        return {"ok": True, "sha": sha, "meta": entry}

    def list_entries(self, limit: int = 50) -> List[Dict[str, Any]]:
        if not LEDGER.exists():
            return []
        lines = LEDGER.read_text(encoding="utf-8").splitlines()[-limit:]
        return [json.loads(x) for x in lines]
