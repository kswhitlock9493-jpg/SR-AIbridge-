#!/usr/bin/env python3
import json, pathlib, os
from common.utils import retrying_check

ROOT = pathlib.Path(__file__).resolve().parents[3]
DIAG = ROOT / "bridge_backend" / "diagnostics"
PARITY = DIAG / "bridge_parity_report.json"
OUT = DIAG / "endpoint_triage_report.json"

BASE = os.getenv("PUBLIC_API_BASE") or os.getenv("VITE_API_BASE") or ""

def main():
    findings = {"ok": True, "tested": [], "missing": [], "base": BASE}
    if not PARITY.exists():
        findings["ok"] = False
        findings["error"] = "parity report missing"
        OUT.write_text(json.dumps(findings, indent=2)); print(json.dumps(findings)); return 1

    data = json.loads(PARITY.read_text())
    # Prefer routes explicitly missing from frontend
    targets = data.get("missing_from_frontend") or []
    # Cap to keep runs quick; can configure via env
    limit = int(os.getenv("ENDPOINT_TRIAGE_LIMIT", "20"))
    targets = targets[:limit]

    for rel in targets:
        if not rel.startswith("/"): rel = "/" + rel
        if BASE:
            url = f"{BASE}{rel}"
            res = retrying_check(url)
            findings["tested"].append({"rel": rel, "url": url, "result": res})
            if not res["ok"]:
                findings["ok"] = False
                findings["missing"].append(rel)
        else:
            findings["ok"] = False
            findings["error"] = "PUBLIC_API_BASE missing"
            break

    OUT.write_text(json.dumps(findings, indent=2))
    print(json.dumps(findings))
    return 0 if findings["ok"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
