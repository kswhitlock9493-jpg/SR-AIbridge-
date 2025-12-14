from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, re
from typing import Iterable, List, Dict, Any, Optional, Tuple

TRUTH_DIR = Path("vault") / "truth"
TRUTH_DIR.mkdir(parents=True, exist_ok=True)

PARSER_DIR = Path("vault") / "parser"
PARSER_LEDGER = PARSER_DIR / "ledger.jsonl"  # {sha, bytes, source, ts}
PARSER_CHUNKS_DIR = PARSER_DIR / "chunks"    # optional subdir; we also accept flat files

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds") + "Z"

def sha256_text(t: str) -> str:
    h = hashlib.sha256(); h.update(t.encode("utf-8", "ignore")); return h.hexdigest()

def write_jsonl(path: Path, records: Iterable[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

def read_jsonl(path: Path) -> List[Dict[str, Any]]:
    if not path.exists(): return []
    with path.open("r", encoding="utf-8") as f:
        return [json.loads(x) for x in f if x.strip()]

def load_parser_ledger() -> List[Dict[str, Any]]:
    return read_jsonl(PARSER_LEDGER)

def load_chunk_text(sha: str) -> Optional[str]:
    # accept chunk files as <sha>.txt either in PARSER_DIR or chunks/
    for base in (PARSER_DIR, PARSER_CHUNKS_DIR):
        p = (base / f"{sha}.txt")
        if p.exists():
            try:
                return p.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                pass
    return None

SENT_SPLIT = re.compile(r'(?<=[.!?])\s+')
CLEAN = re.compile(r'\s+')

def sentences_from_text(txt: str) -> List[str]:
    raw = [s.strip() for s in SENT_SPLIT.split(txt) if s.strip()]
    # normalize whitespace only (keep punctuation for fidelity)
    return [CLEAN.sub(' ', s) for s in raw]

def norm_for_compare(s: str) -> str:
    s = s.lower().strip()
    s = re.sub(r'[\s]+', ' ', s)
    s = re.sub(r'[^a-z0-9\s]', '', s)
    return s

def jaccard(a: str, b: str) -> float:
    A = set(norm_for_compare(a).split())
    B = set(norm_for_compare(b).split())
    if not A or not B: return 0.0
    return len(A & B) / max(1, len(A | B))
