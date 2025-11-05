#!/usr/bin/env python3
import os, sys, json, time
import urllib.request

def ping(url: str) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=6) as r:
            return 200 <= r.status < 300
    except Exception:
        return False

BACKEND = os.getenv("BACKEND_HEALTH_URL", os.getenv("BACKEND_URL", "https://bridge.sr-aibridge.com") + "/api/health")
FRONTEND = os.getenv("FRONTEND_HEALTH_URL", "https://sr-aibridge.netlify.app/.netlify/functions/health")

backend_ok = ping(BACKEND)
frontend_ok = ping(FRONTEND)

status = "stable" if backend_ok and frontend_ok else ("degraded" if backend_ok or frontend_ok else "down")

print(json.dumps({
    "backend_ok": backend_ok,
    "frontend_ok": frontend_ok,
    "status": status,
    "ts": int(time.time())
}, indent=2))

sys.exit(0 if status == "stable" else 1)
