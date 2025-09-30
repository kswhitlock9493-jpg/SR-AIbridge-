from __future__ import annotations
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional
from datetime import datetime
import hashlib, json, re

PARSER_ROOT = Path("vault") / "parser"
CHUNK_DIR = PARSER_ROOT / "chunks"
META_DIR  = PARSER_ROOT / "meta"
LEDGER    = PARSER_ROOT / "ledger.jsonl"

CHUNK_DIR.mkdir(parents=True, exist_ok=True)
META_DIR.mkdir(parents=True, exist_ok=True)
PARSER_ROOT.mkdir(parents=True, exist_ok=True)

def _now() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"

def _sha256(text: str) -> str:
    h = hashlib.sha256(); h.update(text.encode("utf-8", "ignore")); return h.hexdigest()

def _append_ledger(ev: Dict[str, Any]) -> None:
    ev = {"ts": _now(), **ev}
    with LEDGER.open("a", encoding="utf-8") as f:
        f.write(json.dumps(ev) + "\n")

def _meta_path(sha: str) -> Path:
    return META_DIR / f"{sha}.json"

def _chunk_path(sha: str) -> Path:
    return CHUNK_DIR / f"{sha}.txt"

def _load_meta(sha: str) -> Dict[str, Any]:
    mp = _meta_path(sha)
    if not mp.exists():
        raise FileNotFoundError("chunk_not_found")
    try:
        return json.loads(mp.read_text(encoding="utf-8"))
    except Exception:
        return {"sha": sha, "tags": [], "lineage": [], "bytes": 0, "sources": []}

def _save_meta(meta: Dict[str, Any]) -> None:
    sha = meta["sha"]
    (_meta_path(sha)).write_text(json.dumps(meta, indent=2), encoding="utf-8")

@dataclass
class IngestResult:
    ok: bool
    seen: int
    filed: int
    manifest: List[Dict[str, Any]]

class ParserEngine:
    """
    5b: already provided ingest/reassemble.
    5c: enrich with meta/tag/lineage/search/list.
    """

    MAX_SEARCH_BYTES = 250_000   # safety cap for substring search

    def __init__(self):
        CHUNK_DIR.mkdir(parents=True, exist_ok=True)
        META_DIR.mkdir(parents=True, exist_ok=True)
        PARSER_ROOT.mkdir(parents=True, exist_ok=True)

    # ---------- 5b (existing) helpers (summarized; call these from routes) ----------
    def _write_chunk_if_missing(self, text: str, source: Optional[str]) -> Dict[str, Any]:
        sha = _sha256(text)
        cp = _chunk_path(sha)
        created = False
        if not cp.exists():
            cp.write_text(text, encoding="utf-8")
            created = True
            meta = {
                "sha": sha,
                "bytes": len(text.encode("utf-8", "ignore")),
                "tags": [],
                "lineage": [],  # list of {rel, other_sha, dir: "parent"|"child"}
                "sources": list(filter(None, [source])),
                "created_at": _now(),
                "updated_at": _now(),
            }
            _save_meta(meta)
            _append_ledger({"ev": "chunk_created", "sha": sha, "bytes": meta["bytes"], "source": source})
        else:
            # ensure meta exists
            mp = _meta_path(sha)
            if not mp.exists():
                meta = {
                    "sha": sha, "bytes": cp.stat().st_size, "tags": [],
                    "lineage": [], "sources": list(filter(None, [source])),
                    "created_at": _now(), "updated_at": _now(),
                }
                _save_meta(meta)
        return {"sha": sha, "created": created}

    def ingest(self, raw: str, source: Optional[str]=None, max_chunk: int=2000) -> IngestResult:
        # chunk by paragraphs, then size-fit merge
        paras = [p.strip() for p in re.split(r"\n\s*\n", raw or "") if p.strip()]
        chunks: List[str] = []
        buf = ""
        for p in paras:
            if not buf:
                buf = p
            elif len(buf) + 2 + len(p) <= max_chunk:
                buf = f"{buf}\n\n{p}"
            else:
                chunks.append(buf); buf = p
        if buf: chunks.append(buf)

        seen = len(chunks); filed = 0; manifest = []
        for ch in chunks:
            res = self._write_chunk_if_missing(ch, source=source)
            if res["created"]: filed += 1
            manifest.append({"sha": res["sha"], "bytes": len(ch.encode("utf-8","ignore"))})
        return IngestResult(ok=True, seen=seen, filed=filed, manifest=manifest)

    def reassemble(self, sha_list: List[str]) -> str:
        parts = []
        for sha in sha_list:
            cp = _chunk_path(sha)
            if not cp.exists():
                raise FileNotFoundError(f"missing_chunk:{sha}")
            parts.append(cp.read_text(encoding="utf-8"))
        return "\n\n".join(parts)

    # ---------- 5c: NEW CAPABILITIES ----------
    def add_tags(self, sha: str, tags: List[str]) -> Dict[str, Any]:
        meta = _load_meta(sha)
        before = set(meta.get("tags", []))
        after  = sorted(before.union(t.strip() for t in tags if t and t.strip()))
        meta["tags"] = after
        meta["updated_at"] = _now()
        _save_meta(meta)
        _append_ledger({"ev": "tags_added", "sha": sha, "tags": tags})
        return {"sha": sha, "tags": after}

    def remove_tags(self, sha: str, tags: List[str]) -> Dict[str, Any]:
        meta = _load_meta(sha)
        before = set(meta.get("tags", []))
        target = set(t.strip() for t in tags if t and t.strip())
        after  = sorted(list(before - target))
        meta["tags"] = after
        meta["updated_at"] = _now()
        _save_meta(meta)
        _append_ledger({"ev": "tags_removed", "sha": sha, "tags": list(target)})
        return {"sha": sha, "tags": after}

    def link(self, parent_sha: str, child_sha: str, relation: str="derives") -> Dict[str, Any]:
        # ensure both meta exist
        pm = _load_meta(parent_sha)
        cm = _load_meta(child_sha)
        # add bidirectional edges if missing
        def _ensure(edge_list, edge):
            if not any(e["other_sha"] == edge["other_sha"] and e["rel"] == edge["rel"] and e["dir"] == edge["dir"]
                       for e in edge_list):
                edge_list.append(edge)

        _ensure(pm["lineage"], {"rel": relation, "other_sha": child_sha, "dir": "child"})
        _ensure(cm["lineage"], {"rel": relation, "other_sha": parent_sha, "dir": "parent"})
        pm["updated_at"] = _now(); cm["updated_at"] = _now()
        _save_meta(pm); _save_meta(cm)
        _append_ledger({"ev": "lineage_linked", "parent": parent_sha, "child": child_sha, "rel": relation})
        return {"ok": True, "parent": parent_sha, "child": child_sha, "rel": relation}

    def manifest(self, sha: str) -> Dict[str, Any]:
        meta = _load_meta(sha)
        text = ""
        cp = _chunk_path(sha)
        if cp.exists():
            # cap read for safety
            text = cp.read_text(encoding="utf-8")[: self.MAX_SEARCH_BYTES]
        return {"meta": meta, "preview": text}

    def list(self, tag: Optional[str]=None, source: Optional[str]=None, limit: int=100) -> Dict[str, Any]:
        items: List[Dict[str, Any]] = []
        for mp in META_DIR.glob("*.json"):
            try:
                m = json.loads(mp.read_text(encoding="utf-8"))
            except Exception:
                continue
            if tag and tag not in m.get("tags", []): 
                continue
            if source and source not in (m.get("sources") or []):
                continue
            items.append({"sha": m["sha"], "tags": m.get("tags", []), "bytes": m.get("bytes", 0),
                          "updated_at": m.get("updated_at"), "sources": m.get("sources", [])})
            if len(items) >= limit:
                break
        # newest-first
        items.sort(key=lambda x: (x.get("updated_at") or ""), reverse=True)
        return {"items": items}

    def search(self, q: str, limit: int=50) -> Dict[str, Any]:
        ql = (q or "").strip().lower()
        if len(ql) < 2:
            return {"items": []}
        matches: List[Dict[str, Any]] = []
        for mp in META_DIR.glob("*.json"):
            m = json.loads(mp.read_text(encoding="utf-8"))
            sha = m["sha"]
            # search tags & sources quickly
            hay_meta = " ".join(m.get("tags", []) + (m.get("sources") or [])).lower()
            score = 0.0
            if ql in hay_meta:
                score += 0.5
            # search content (bounded)
            cp = _chunk_path(sha)
            if cp.exists():
                txt = cp.read_text(encoding="utf-8")[: self.MAX_SEARCH_BYTES]
                if ql in txt.lower():
                    score += 1.0
            if score > 0:
                matches.append({
                    "sha": sha,
                    "score": round(score, 3),
                    "tags": m.get("tags", []),
                    "snippet": (txt[:300] if score > 0 and cp.exists() else ""),
                })
            if len(matches) >= limit:
                break
        matches.sort(key=lambda x: x["score"], reverse=True)
        return {"items": matches}