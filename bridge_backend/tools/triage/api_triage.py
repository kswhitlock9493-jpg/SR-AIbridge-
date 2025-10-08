#!/usr/bin/env python3
import os, json, pathlib
from common.utils import retrying_check

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUTDIR = ROOT / "bridge_backend" / "diagnostics"
OUTDIR.mkdir(parents=True, exist_ok=True)
OUT = OUTDIR / "api_triage_report.json"

BASE = os.getenv("PUBLIC_API_BASE") or os.getenv("REACT_APP_API_URL") or os.getenv("VITE_API_BASE")
if BASE and BASE.endswith("/"): BASE = BASE[:-1]

HEALTH_PATHS = [
    "/api/health", "/api/v1/health", "/healthz",
    "/api/_meta", "/api/version"
]

def main():
    if not BASE:
        data = {"ok": False, "reason": "PUBLIC_API_BASE missing"}
        OUT.write_text(json.dumps(data, indent=2)); print(json.dumps(data)); return 2
    results = []
    for p in HEALTH_PATHS:
        url = f"{BASE}{p}"
        results.append({"path": p, "result": retrying_check(url)})
    ok = any(r["result"]["ok"] for r in results)
    report = {"ok": ok, "base": BASE, "checks": results}
    OUT.write_text(json.dumps(report, indent=2))
    print(json.dumps(report))
    return 0 if ok else 1

if __name__ == "__main__":
    raise SystemExit(main())
