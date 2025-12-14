from __future__ import annotations
from typing import List, Dict, Any
from .utils import TRUTH_DIR, now_iso, jaccard, norm_for_compare, write_jsonl, sha256_text

TRUTHS_LOG = TRUTH_DIR / "truths.jsonl"

def bind_candidates(candidates: List[Dict[str, Any]], similarity: float = 0.72) -> Dict[str, Any]:
    """
    Merge near-duplicate/overlapping candidate facts.
    Input format (from finder): {id, fact, sources:[{sha,ts,source}]}
    """
    clusters: List[Dict[str, Any]] = []
    for c in candidates:
        fact = c.get("fact","")
        srcs = c.get("sources",[])
        placed = False
        for cl in clusters:
            if jaccard(cl["canonical"], fact) >= similarity:
                # prefer the longer/more-informative sentence as canonical
                if len(fact) > len(cl["canonical"]):
                    cl["canonical"] = fact
                cl["variants"].append(fact)
                cl["sources"].extend(srcs)
                placed = True
                break
        if not placed:
            clusters.append({"canonical": fact, "variants": [fact], "sources": list(srcs)})

    truths = []
    for cl in clusters:
        canon = cl["canonical"].strip()
        truth_id = sha256_text(norm_for_compare(canon))[:16]
        # dedupe sources by sha
        seen = set()
        sources = []
        for s in cl["sources"]:
            k = (s.get("sha"), s.get("ts"))
            if k in seen: continue
            seen.add(k); sources.append(s)
        truths.append({
            "truth_id": truth_id,
            "statement": canon,
            "sources": sources,
            "variants": sorted(set(cl["variants"]))
        })

    run = {"ts": now_iso(), "similarity": similarity, "truths": truths, "count": len(truths)}
    write_jsonl(TRUTHS_LOG, [run])
    return run

def list_truths(limit: int = 50) -> Dict[str, Any]:
    rows = []
    p = TRUTHS_LOG
    if p.exists():
        with p.open("r", encoding="utf-8") as f:
            rows = [line for line in f if line.strip()]
    out = []
    for line in reversed(rows):
        try:
            j = __import__("json").loads(line)
        except Exception:
            continue
        out.extend(j.get("truths", []))
        if len(out) >= limit:
            break
    return {"truths": out[:limit], "count": len(out[:limit])}
