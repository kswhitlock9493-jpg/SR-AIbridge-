from __future__ import annotations
from typing import Dict, Any, List
from .utils import read_jsonl, TRUTH_DIR, norm_for_compare, sha256_text

TRUTHS_LOG = TRUTH_DIR / "truths.jsonl"

def cite(statement: str) -> Dict[str, Any]:
    """
    Find best matching truth (by normalized string + Jaccard against variants),
    return its sources/citations. If none, return empty list.
    """
    import json
    norm = norm_for_compare(statement)
    rows = read_jsonl(TRUTHS_LOG)
    best = None
    best_j = 0.0

    from .utils import jaccard
    for run in rows:
        for t in run.get("truths", []):
            scores = [jaccard(statement, t.get("statement",""))] + [jaccard(statement, v) for v in t.get("variants",[])]
            j = max(scores) if scores else 0.0
            if j > best_j:
                best_j = j; best = t

    return {
        "query": statement,
        "match_score": round(best_j, 4),
        "truth": best or None,
        "citations": (best or {}).get("sources", [])
    }
