#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""
Comprehensive triage matrix - validates backend endpoints and API surface
"""
import json, os, time, urllib.request
from pathlib import Path

BASE = os.getenv("BRIDGE_BASE", "https://sr-aibridge.onrender.com")
OUT = Path("bridge_backend/diagnostics/triage_matrix.ndjson")
OUT.parent.mkdir(parents=True, exist_ok=True)

ENDPOINTS = [
    ("/api/health", True),
    ("/api/version", False),
    ("/api/routes", False),
]

def ping(path, timeout=6):
    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(f"{BASE}{path}", timeout=timeout) as r:
            ms = int((time.perf_counter()-t0)*1000)
            return True, r.getcode(), ms, None
    except Exception as e:
        ms = int((time.perf_counter()-t0)*1000)
        return False, None, ms, str(e)

def main():
    failures = 0; required_total = 0
    with OUT.open("w") as f:
        for path, required in ENDPOINTS:
            ok, code, ms, err = ping(path)
            f.write(json.dumps({"path":path,"required":required,"ok":ok,"code":code,"ms":ms,"err":err}) + "\n")
            if required:
                required_total += 1
                if not ok:
                    failures += 1
    # Pass if ≥1 required endpoints and at least 80% of required succeeded
    passed = required_total > 0 and failures/required_total <= 0.20
    print(f"Wrote {OUT} | required: {required_total} | failures: {failures} | pass: {passed}")
    return 0 if passed else 2

if __name__ == "__main__":
    raise SystemExit(main())
