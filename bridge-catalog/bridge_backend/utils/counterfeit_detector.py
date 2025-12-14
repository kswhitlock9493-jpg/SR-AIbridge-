from __future__ import annotations
import re, hashlib
from pathlib import Path
from typing import Dict, List, Tuple

TOKEN_RE = re.compile(r"\w+", re.UNICODE)

def _normalize(code: str) -> List[str]:
    code = code.replace("\r", "\n")
    code = "\n".join(line.split("#", 1)[0] for line in code.splitlines())  # strip Python-ish comments
    return TOKEN_RE.findall(code.lower())

def _shingles(tokens: List[str], k: int = 6) -> set:
    if len(tokens) < k: return set()
    return set(" ".join(tokens[i:i+k]) for i in range(len(tokens)-k+1))

def jaccard(a: set, b: set) -> float:
    if not a and not b: return 1.0
    u = len(a|b)
    return (len(a&b) / u) if u else 0.0

def compare_text(a: str, b: str) -> float:
    return jaccard(_shingles(_normalize(a)), _shingles(_normalize(b)))

def best_match_against_corpus(target: Path, corpus_dir: Path, patterns=(".py",".js",".ts",".tsx")) -> Dict:
    if not target.suffix.lower() in patterns: return {"score": 0.0, "match_path": None}
    try:
        t = target.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return {"score": 0.0, "match_path": None}
    best = {"score": 0.0, "match_path": None}
    for p in corpus_dir.rglob("*"):
        if not p.is_file() or p == target or p.suffix.lower() not in patterns: 
            continue
        try:
            s = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        score = compare_text(t, s)
        if score > best["score"]:
            best = {"score": score, "match_path": str(p.relative_to(corpus_dir))}
    return best
