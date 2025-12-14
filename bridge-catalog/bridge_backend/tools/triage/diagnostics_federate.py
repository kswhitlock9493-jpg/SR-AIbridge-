#!/usr/bin/env python3
import json, pathlib, time, os, asyncio

ROOT = pathlib.Path(__file__).resolve().parents[3]
DIAG = ROOT / "bridge_backend" / "diagnostics"
OUT = DIAG / "triage_federation_report.json"

FILES = [
    "api_triage_report.json",
    "endpoint_triage_report.json",
    "firewall_report.json",  # optional, if present include
]

MAX_WAIT_S = int(os.getenv("FEDERATION_MAX_WAIT_S", "120"))

def read_json_safe(path): 
    try: return json.loads(path.read_text())
    except Exception: return {"ok": False, "error": "unreadable"}

async def publish_federation_event(report):
    """Publish federation event to genesis bus for autonomy engine integration"""
    try:
        import sys
        sys.path.insert(0, str(ROOT / "bridge_backend"))
        from genesis.bus import genesis_bus
        
        if genesis_bus.is_enabled():
            await genesis_bus.publish("triage.diagnostics", {
                "type": "diagnostics_federation",
                "source": "triage",
                "report": report,
            })
    except Exception as e:
        # Silently fail if genesis bus not available (e.g., during CI)
        pass

def main():
    DIAG.mkdir(parents=True, exist_ok=True)
    # allow other jobs to finish writing
    waited = 0
    while waited < MAX_WAIT_S:
        if all((DIAG/f).exists() for f in FILES if f != "firewall_report.json") and (True):
            break
        time.sleep(2); waited += 2

    bundle = {}
    overall_ok = True
    for f in FILES:
        p = DIAG / f
        if p.exists():
            bundle[f] = read_json_safe(p)
            if bundle[f].get("ok") is False:
                overall_ok = False
        else:
            bundle[f] = {"ok": True, "note": "not-generated"}

    report = {"ok": overall_ok, "waited_s": waited, "reports": bundle}
    OUT.write_text(json.dumps(report, indent=2))
    print(json.dumps(report))
    
    # Publish event to genesis bus for autonomy integration
    try:
        asyncio.run(publish_federation_event(report))
    except Exception:
        pass  # Ignore errors in event publishing
    
    return 0 if overall_ok else 1

if __name__ == "__main__":
    raise SystemExit(main())
