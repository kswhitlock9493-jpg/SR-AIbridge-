from __future__ import annotations
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
import json, uuid, hashlib

from bridge_core.engines.leviathan.service import LeviathanEngine

VAULT = Path("vault")
CREATIVITY_DIR = VAULT / "creativity"
CREATIVITY_DIR.mkdir(parents=True, exist_ok=True)
ASSETS_DIR = CREATIVITY_DIR  # Alias for compatibility

def now_iso() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"

def sha256_text(t: str) -> str:
    return hashlib.sha256(t.encode("utf-8", "ignore")).hexdigest()

@dataclass
class CreativeAsset:
    sha: str
    title: str
    text: str
    tags: List[str]
    source: str
    created_at: str

    def to_dict(self):
        return asdict(self)

class CreativityBay:
    def __init__(self, vault_dir: Path = CREATIVITY_DIR):
        self.vault = vault_dir
        self.vault.mkdir(parents=True, exist_ok=True)
        self.leviathan = LeviathanEngine()

    def ingest(self, title: str, text: str, tags: Optional[List[str]], source: str) -> CreativeAsset:
        sha = sha256_text(text)
        ts = now_iso()
        asset = CreativeAsset(
            sha=sha, title=title, text=text,
            tags=tags or [], source=source, created_at=ts
        )
        # persist text + metadata
        (self.vault / f"{sha}.txt").write_text(text, encoding="utf-8")
        (self.vault / f"{sha}.json").write_text(json.dumps(asset.to_dict(), indent=2), encoding="utf-8")
        return asset

    def search(self, query: str, tags: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        results = []
        for f in self.vault.glob("*.json"):
            try:
                meta = json.loads(f.read_text(encoding="utf-8"))
                # Check if query matches text or title
                if query.lower() in meta.get("text", "").lower() or query.lower() in meta.get("title", "").lower():
                    # If tags filter is specified, check if all requested tags are present
                    if tags:
                        if not set(tags).issubset(set(meta.get("tags", []))):
                            continue
                    results.append(meta)
            except Exception:
                continue
        return results

    def list_entries(self, limit: int = 50) -> List[Dict[str, Any]]:
        entries = []
        for f in sorted(self.vault.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
            if len(entries) >= limit:
                break
            try:
                meta = json.loads(f.read_text(encoding="utf-8"))
                entries.append(meta)
            except Exception:
                continue
        return entries
