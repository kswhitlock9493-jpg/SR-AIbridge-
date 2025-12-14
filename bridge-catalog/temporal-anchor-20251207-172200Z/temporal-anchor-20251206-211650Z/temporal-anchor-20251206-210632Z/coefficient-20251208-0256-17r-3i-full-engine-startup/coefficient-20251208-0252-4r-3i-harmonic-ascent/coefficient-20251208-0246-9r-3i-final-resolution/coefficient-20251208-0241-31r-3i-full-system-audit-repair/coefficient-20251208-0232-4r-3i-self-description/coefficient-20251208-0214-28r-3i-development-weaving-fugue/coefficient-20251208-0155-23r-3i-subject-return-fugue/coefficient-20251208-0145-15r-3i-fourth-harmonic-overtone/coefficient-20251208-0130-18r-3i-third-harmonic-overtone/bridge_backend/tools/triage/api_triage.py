#!/usr/bin/env python3
import os, json, pathlib, asyncio
from common.utils import retrying_check

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUTDIR = ROOT / "bridge_backend" / "diagnostics"
OUTDIR.mkdir(parents=True, exist_ok=True)
OUT = OUTDIR / "api_triage_report.json"

BASE = os.getenv("PUBLIC_API_BASE") or os.getenv("REACT_APP_API_URL") or os.getenv("VITE_API_BASE")
if BASE and BASE.endswith("/"): BASE = BASE[:-1]

HEALTH_PATHS = [
    "/health", "/health/full", "/api/bridge/health",
    "/api/status", "/"
]

async def publish_triage_event(report):
    """Publish triage event to genesis bus for autonomy engine integration"""
    try:
        import sys
        sys.path.insert(0, str(ROOT / "bridge_backend"))
        from genesis.bus import genesis_bus
        
        if genesis_bus.is_enabled():
            await genesis_bus.publish("triage.api", {
                "type": "api_triage",
                "source": "triage",
                "report": report,
            })
    except Exception as e:
        # Silently fail if genesis bus not available (e.g., during CI)
        pass

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
    
    # Publish event to genesis bus for autonomy integration
    try:
        asyncio.run(publish_triage_event(report))
    except Exception:
        pass  # Ignore errors in event publishing
    
    return 0 if ok else 1

if __name__ == "__main__":
    raise SystemExit(main())
