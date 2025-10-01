from __future__ import annotations
from pathlib import Path
from typing import List, Dict, Any, Optional
import json
import datetime as dt

# Creativity assets (from 6g/6h)
from ..creativity.service import ASSETS_DIR  # vault/creativity/assets

# Parser + Truth utilities (from Section 5)
from ..truth.utils import (
    TRUTH_DIR, PARSER_DIR, PARSER_LEDGER,
    read_jsonl, load_chunk_text, now_iso
)

class LeviathanEngine:
    """
    Unified deep search across Bridge planes:
      - creativity:  assets in vault/creativity/assets/*.json
      - parser:      sentences from Parser ledger chunks
      - truth:       bound truths from Truth Engine
    Tag filtering applies where tags exist (creativity today; others optional).
    """

    def __init__(self, vault_root: Path = Path("vault")):
        self.vault = vault_root

    # -----------------------------
    # Loaders for each plane
    # -----------------------------

    def _load_creativity_assets(self) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []
        for f in ASSETS_DIR.glob("*.json"):
            try:
                meta = json.loads(f.read_text(encoding="utf-8"))
                # expected: {sha,title,text,tags,source,created_at}
                out.append(meta)
            except Exception:
                continue
        return out

    def _load_parser_sentences(self) -> List[Dict[str, Any]]:
        """
        Expand parser ledger into sentence-level docs with provenance.
        Uses the same sentence splitter as Truth Engine utils.
        """
        from ..truth.utils import sentences_from_text  # local import to avoid cycles
        ledger = read_jsonl(PARSER_LEDGER)
        rows: List[Dict[str, Any]] = []
        for row in ledger:
            sha = row.get("sha") or row.get("hash") or row.get("id")
            if not sha:
                continue
            txt = load_chunk_text(sha) or ""
            if not txt.strip():
                continue
            for sent in sentences_from_text(txt):
                rows.append({
                    "plane": "parser",
                    "sha": sha,
                    "title": (row.get("source") or "parser") + " • sentence",
                    "text": sent,
                    "tags": row.get("tags", []),          # optional
                    "source": row.get("source", "parser"),
                    "created_at": row.get("ts") or now_iso(),
                    "path": f"{PARSER_DIR}/{sha}.txt"
                })
        return rows

    def _load_truths(self) -> List[Dict[str, Any]]:
        truths_file = TRUTH_DIR / "truths.jsonl"
        rows: List[Dict[str, Any]] = []
        for t in read_jsonl(truths_file):
            # expected truth entry (from 5f Binder): { "truth": "...", "prov":[{sha,source,ts},...], "created_at": ... }
            canon = t.get("truth") or ""
            created = t.get("created_at") or now_iso()
            tags = t.get("tags", [])  # optional
            prov = t.get("prov", [])
            sha_hint = prov[0]["sha"] if prov else None
            rows.append({
                "plane": "truth",
                "sha": sha_hint,
                "title": "Truth • canonical",
                "text": canon,
                "tags": tags,
                "source": "truth_engine",
                "created_at": created,
                "path": str(TRUTH_DIR / "truths.jsonl"),
                "prov": prov
            })
        return rows

    # -----------------------------
    # Search helpers
    # -----------------------------

    @staticmethod
    def _match_text(q: str, text: str, title: Optional[str] = None) -> bool:
        ql = (q or "").strip().lower()
        if not ql:
            return False
        tl = (text or "").lower()
        if ql in tl:
            return True
        if title and ql in (title or "").lower():
            return True
        return False

    @staticmethod
    def _tags_ok(required: Optional[List[str]], have: Optional[List[str]]) -> bool:
        if not required:
            return True
        have_set = set(have or [])
        return set(required).issubset(have_set)

    @staticmethod
    def _snippet(text: str, limit: int = 200) -> str:
        if not text:
            return ""
        return text[:limit] + ("..." if len(text) > limit else "")

    @staticmethod
    def _parse_ts(ts: str) -> dt.datetime:
        try:
            return dt.datetime.fromisoformat(ts.replace("Z", "+00:00"))
        except Exception:
            return dt.datetime.utcnow().replace(tzinfo=dt.timezone.utc)

    # -----------------------------
    # Public search
    # -----------------------------

    def search(
        self,
        query: str,
        tags: Optional[List[str]] = None,
        limit: int = 50,
        planes: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Unified search. planes default: ["creativity","parser","truth"]
        """
        planes = planes or ["creativity", "parser", "truth"]
        bag: List[Dict[str, Any]] = []

        # creativity
        if "creativity" in planes:
            for meta in self._load_creativity_assets():
                if self._match_text(query, meta.get("text", ""), meta.get("title", "")) \
                   and self._tags_ok(tags, meta.get("tags")):
                    bag.append({
                        "plane": "creativity",
                        "sha": meta.get("sha"),
                        "title": meta.get("title"),
                        "tags": meta.get("tags", []),
                        "source": meta.get("source"),
                        "created_at": meta.get("created_at"),
                        "snippet": self._snippet(meta.get("text", "")),
                        "path": meta.get("path")  # optional
                    })

        # parser
        if "parser" in planes:
            for row in self._load_parser_sentences():
                if self._match_text(query, row["text"], row["title"]) \
                   and self._tags_ok(tags, row.get("tags", [])):
                    bag.append({
                        "plane": "parser",
                        "sha": row["sha"],
                        "title": row["title"],
                        "tags": row.get("tags", []),
                        "source": row["source"],
                        "created_at": row["created_at"],
                        "snippet": self._snippet(row["text"]),
                        "path": row["path"]
                    })

        # truth
        if "truth" in planes:
            for row in self._load_truths():
                if self._match_text(query, row["text"], row["title"]) \
                   and self._tags_ok(tags, row.get("tags", [])):
                    bag.append({
                        "plane": "truth",
                        "sha": row.get("sha"),
                        "title": row["title"],
                        "tags": row.get("tags", []),
                        "source": row["source"],
                        "created_at": row["created_at"],
                        "snippet": self._snippet(row["text"]),
                        "path": row["path"],
                        "prov": row.get("prov", [])
                    })

        # Sort newest first, then by plane priority (truth > parser > creativity)
        priority = {"truth": 0, "parser": 1, "creativity": 2}
        bag.sort(
            key=lambda r: (
                self._parse_ts(r.get("created_at") or now_iso()),
                -priority.get(r.get("plane"), 9)
            ),
            reverse=True
        )

        return bag[: max(1, min(limit, 200))]
