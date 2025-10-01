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
    def __init__(self):
        _init_db()

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

    def search(self, query: str, namespaces: Optional[List[str]] = None,
               limit: int = 20) -> List[Dict[str, Any]]:
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
        return [{"sha": r[0], "namespace": r[1], "text": r[2], "source": r[3], "ts": r[4]} for r in rows]

    def sources(self) -> List[str]:
        con = sqlite3.connect(DB)
        cur = con.cursor()
        cur.execute("SELECT DISTINCT namespace FROM docs")
        rows = [r[0] for r in cur.fetchall()]
        con.close()
        return rows
