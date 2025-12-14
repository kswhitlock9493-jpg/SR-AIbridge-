from __future__ import annotations
from typing import List, Dict, Any, Optional
from .utils import (
    load_parser_ledger, load_chunk_text, sentences_from_text,
    now_iso, sha256_text, TRUTH_DIR, write_jsonl
)
from datetime import datetime, timezone

CANDIDATES_LOG = TRUTH_DIR / "candidates.jsonl"

def _score(ts: str, freq: int) -> float:
    # recency (linear decay) + frequency
    try:
        t = datetime.fromisoformat(ts.replace("Z",""))
    except Exception:
        return float(freq)
    age_days = max(0.0, (datetime.now(timezone.utc) - t).total_seconds() / 86400.0)
    rec = max(0.0, 1.0 - (age_days / 30.0))  # 30d horizon
    return freq + rec

def find_candidates(query: Optional[str] = None, limit: int = 50) -> Dict[str, Any]:
    ledger = load_parser_ledger()
    freq: Dict[str, int] = {}
    first_ts: Dict[str, str] = {}
    prov: Dict[str, List[Dict[str, Any]]] = {}

    q = (query or "").strip().lower()

    for row in ledger:
        sha = row.get("sha") or row.get("hash") or row.get("id")
        if not sha: continue
        txt = load_chunk_text(sha)
        if not txt: continue
        for sent in sentences_from_text(txt):
            if q and q not in sent.lower():
                continue
            key = sent
            freq[key] = freq.get(key, 0) + 1
            first_ts.setdefault(key, row.get("ts") or row.get("timestamp") or now_iso())
            prov.setdefault(key, []).append({"sha": sha, "ts": row.get("ts"), "source": row.get("source")})

    scored = sorted(
        [{"fact": s, "score": _score(first_ts.get(s, now_iso()), f), "freq": f, "first_ts": first_ts.get(s), "prov": prov.get(s, [])}
         for s, f in freq.items()],
        key=lambda x: (x["score"], x["freq"]), reverse=True
    )[:limit]

    run = {
        "ts": now_iso(),
        "query": query or "",
        "limit": limit,
        "count": len(scored),
        "candidates": [
            {"id": sha256_text(c["fact"]), "fact": c["fact"], "freq": c["freq"], "first_ts": c["first_ts"], "score": c["score"],
             "sources": c["prov"]}
            for c in scored
        ]
    }
    write_jsonl(CANDIDATES_LOG, [run])
    return run
