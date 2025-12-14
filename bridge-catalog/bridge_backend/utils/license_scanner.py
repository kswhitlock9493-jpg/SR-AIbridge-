from __future__ import annotations
import re, hashlib
from pathlib import Path
from typing import Dict, List, Optional

LICENSE_SIGNATURES: Dict[str, List[str]] = {
    "MIT": ["permission is hereby granted, free of charge"],
    "Apache-2.0": ["apache license, version 2.0", "http://www.apache.org/licenses/"],
    "BSD-3-Clause": ["redistribution and use in source and binary forms"],
    "GPL-2.0": ["gnu general public license", "version 2"],
    "GPL-3.0": ["gnu general public license", "version 3"],
    "AGPL-3.0": ["gnu affero general public license"],
}

SPDX_RE = re.compile(r"spdx-license-identifier:\s*([A-Za-z0-9\-\._+]+)", re.I)

def _safe_read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")

def guess_license_for_text(text: str) -> Optional[str]:
    m = SPDX_RE.search(text)
    if m: return m.group(1)
    lt = text.lower()
    for key, sigs in LICENSE_SIGNATURES.items():
        for s in sigs:
            if s in lt: return key
    return None

def scan_files(root: Path, files: List[str]) -> Dict:
    out = {"files": [], "summary": {"counts_by_license": {}}}
    for rel in files:
        p = (root / rel)
        if not p.exists() or p.is_dir(): 
            continue
        text = _safe_read(p)
        lic = guess_license_for_text(text)
        sha = hashlib.sha256(p.read_bytes()).hexdigest()
        out["files"].append({"path": rel, "license_guess": lic or "UNKNOWN", "sha256": sha, "size": p.stat().st_size})
        key = lic or "UNKNOWN"
        out["summary"]["counts_by_license"][key] = out["summary"]["counts_by_license"].get(key, 0) + 1
    return out
