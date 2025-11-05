#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""
Backend smoke test - validates core backend health endpoints
"""
import json, os, sys, time, urllib.request
from pathlib import Path

BASE = os.getenv("BRIDGE_BASE", os.getenv("BACKEND_URL", "https://bridge.sr-aibridge.com"))
OUT = Path("bridge_backend/diagnostics/triage_runtime_metrics.json")
OUT.parent.mkdir(parents=True, exist_ok=True)

def get(path, timeout=8):
    with urllib.request.urlopen(f"{BASE}{path}", timeout=timeout) as r:
        return r.getcode(), r.read()

def get_json(path):
    code, body = get(path)
    return code, json.loads(body.decode())

def main():
    start = time.time()
    result = {"base": BASE, "ok": True, "checks": [], "started": start}
    budget_fail = False

    # `/api/health` (required, retry)
    from time import sleep
    for attempt in range(6):
        try:
            code, _ = get("/api/health", timeout=6)
            ok = (code == 200)
            result["checks"].append({"name":"health","ok":ok,"code":code,"attempt":attempt+1})
            if ok: break
        except Exception as e:
            result["checks"].append({"name":"health","ok":False,"err":str(e),"attempt":attempt+1})
        sleep(min(5, 0.25 * (2**attempt)))
    else:
        budget_fail = True

    # `/api/version` (optional but informative)
    try:
        code, ver = get_json("/api/version")
        result["checks"].append({"name":"version","ok":code==200,"payload":ver})
    except Exception as e:
        result["checks"].append({"name":"version","ok":False,"err":str(e)})

    # `/api/routes` (optional)
    try:
        code, routes = get_json("/api/routes")
        result["checks"].append({"name":"routes","ok":code==200,"count":routes.get("count",0)})
    except Exception as e:
        result["checks"].append({"name":"routes","ok":False,"err":str(e)})

    result["duration_s"] = round(time.time()-start, 3)
    result["ok"] = not budget_fail
    OUT.write_text(json.dumps(result, indent=2))
    print(f"Wrote {OUT}")
    sys.exit(0 if result["ok"] else 2)

if __name__ == "__main__":
    main()
