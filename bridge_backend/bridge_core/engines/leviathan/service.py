from __future__ import annotations
from pathlib import Path
from datetime import datetime
import sqlite3, hashlib, json, uuid
from typing import Dict, Any, List, Optional

VAULT = Path("vault")
LEVIATHAN_DIR = VAULT / "leviathan"
LEVIATHAN_DIR.mkdir(parents=True, exist_ok=True)
LEDGER = LEVIATHAN_DIR / "ledger.jsonl"
DB = LEVIATHAN_DIR / "index.db"

# Import creativity assets directory for global search
CREATIVITY_DIR = VAULT / "creativity"
ASSETS_DIR = CREATIVITY_DIR

def now_iso() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"

def sha256_text(t: str) -> str:
    return hashlib.sha256(t.encode("utf-8", "ignore")).hexdigest()

def _init_db():
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS docs (
        sha TEXT PRIMARY KEY,
        namespace TEXT,
        text TEXT,
        source TEXT,
        ts TEXT
    )""")
    cur.execute("""CREATE VIRTUAL TABLE IF NOT EXISTS docs_idx USING fts5(
        sha, namespace, text, source, ts
    )""")
    con.commit()
    con.close()

class LeviathanEngine:
    def __init__(self, vault_root: Path = VAULT):
        _init_db()
        self.vault = vault_root

    def _load_creativity_assets(self) -> List[Dict[str, Any]]:
        """Load creativity assets from vault for global search"""
        out = []
        for f in ASSETS_DIR.glob("*.json"):
            try:
                meta = json.loads(f.read_text(encoding="utf-8"))
                out.append(meta)
            except Exception:
                continue
        return out

    def index(self, text: str, namespace: str, source: str) -> Dict[str, Any]:
        sha = sha256_text(text)
        ts = now_iso()
        con = sqlite3.connect(DB)
        cur = con.cursor()
        cur.execute("INSERT OR REPLACE INTO docs VALUES (?,?,?,?,?)",
                    (sha, namespace, text, source, ts))
        cur.execute("INSERT OR REPLACE INTO docs_idx VALUES (?,?,?,?,?)",
                    (sha, namespace, text, source, ts))
        con.commit()
        con.close()
        with LEDGER.open("a", encoding="utf-8") as f:
            f.write(json.dumps({"sha": sha, "namespace": namespace,
                                "source": source, "ts": ts}) + "\n")
        return {"ok": True, "sha": sha, "namespace": namespace, "ts": ts}

    def search(self, query: str, tags: Optional[List[str]] = None, 
               namespaces: Optional[List[str]] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Global deep search across vault assets + creativity bay with optional tag filtering.
        """
        results = []

        # Search creativity bay with tag filtering
        for meta in self._load_creativity_assets():
            if query.lower() in meta.get("text", "").lower() or query.lower() in meta.get("title", "").lower():
                # If tags filter is specified, check if all requested tags are present
                if tags:
                    if not set(tags).issubset(set(meta.get("tags", []))):
                        continue
                results.append({
                    "sha": meta.get("sha", ""),
                    "title": meta.get("title", ""),
                    "tags": meta.get("tags", []),
                    "source": meta.get("source", ""),
                    "created_at": meta.get("created_at", ""),
                    "snippet": meta.get("text", "")[:200] + ("..." if len(meta.get("text", "")) > 200 else "")
                })

        # Also search traditional indexed docs (namespace-based search)
        con = sqlite3.connect(DB)
        cur = con.cursor()
        ns_filter = ""
        params = [query]
        if namespaces:
            placeholders = ",".join("?" for _ in namespaces)
            ns_filter = f"AND namespace IN ({placeholders})"
            params.extend(namespaces)
        cur.execute(f"SELECT sha, namespace, text, source, ts FROM docs_idx WHERE text MATCH ? {ns_filter} LIMIT ?",
                    (*params, limit))
        rows = cur.fetchall()
        con.close()
        
        # Add indexed docs to results (these don't have tags)
        for r in rows:
            results.append({
                "sha": r[0], 
                "namespace": r[1], 
                "text": r[2], 
                "source": r[3], 
                "ts": r[4]
            })

        # Sort by created_at/ts if available, newest first
        results.sort(key=lambda r: r.get("created_at") or r.get("ts", ""), reverse=True)
        return results[:limit]

    def sources(self) -> List[str]:
        con = sqlite3.connect(DB)
        cur = con.cursor()
        cur.execute("SELECT DISTINCT namespace FROM docs")
        rows = [r[0] for r in cur.fetchall()]
        con.close()
        return rows
