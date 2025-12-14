import json, hashlib, os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

try:
    from utils.license_scanner import scan_files
    from utils.counterfeit_detector import best_match_against_corpus
    from utils.scan_policy import load_policy
    from utils.signing import sign_payload
except ImportError:
    from bridge_backend.utils.license_scanner import scan_files
    from bridge_backend.utils.counterfeit_detector import best_match_against_corpus
    from bridge_backend.utils.scan_policy import load_policy
    from bridge_backend.utils.signing import sign_payload

SCAN_DIR = Path("bridge_backend/scan_reports")

def run_combined_scan(root: str, changed_files: List[str], pr: int|None, commit: str|None) -> Dict:
    rootp = Path(root)
    policy = load_policy()
    lic = scan_files(rootp, changed_files)
    cf: List[Dict] = []
    corpus = rootp / "bridge_backend"  # internal corpus (fast + private)
    for rel in changed_files:
        p = rootp / rel
        if not p.exists() or p.is_dir(): 
            continue
        if any(str(p).find(ex) >= 0 for ex in policy["scan_exclude_paths"]): 
            continue
        match = best_match_against_corpus(p, corpus)
        cf.append({"path": rel, **match})
    
    combined = {
        "pr": pr, "commit": commit,
        "license": lic,
        "counterfeit": cf,
        "meta": {"timestamp": datetime.now(timezone.utc).isoformat()+"Z"}
    }
    
    # Policy evaluation
    state = "ok"
    blocked = set(policy["blocked_licenses"])
    for f in lic["files"]:
        if f["license_guess"] in blocked:
            state = "blocked"; break
    if state != "blocked":
        max_hit = max((x["score"] for x in cf), default=0.0)
        if max_hit >= policy["thresholds"]["counterfeit_confidence_block"]:
            state = "blocked"
        elif max_hit >= policy["thresholds"]["counterfeit_confidence_flag"]:
            state = "flagged"
    
    combined["policy_state"] = state
    signed = sign_payload(combined)
    SCAN_DIR.mkdir(parents=True, exist_ok=True)
    sid = hashlib.sha256(json.dumps(combined, sort_keys=True).encode()).hexdigest()[:16]
    out = SCAN_DIR / f"{sid}.json"
    out.write_text(json.dumps(signed, indent=2))
    combined["id"] = sid
    return {"id": sid, "state": state, "path": str(out), "signed": signed}

def list_scans() -> List[Dict]:
    SCAN_DIR.mkdir(parents=True, exist_ok=True)
    out = []
    for p in sorted(SCAN_DIR.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True)[:200]:
        try:
            data = json.loads(p.read_text())
            payload = data.get("payload", {})
            out.append({"id": p.stem, "policy_state": payload.get("policy_state","ok"),
                        "meta": payload.get("meta",{}), "pr": payload.get("pr"), "commit": payload.get("commit")})
        except Exception:
            continue
    return out

def read_scan(scan_id: str) -> Dict:
    p = SCAN_DIR / f"{scan_id}.json"
    return json.loads(p.read_text())
