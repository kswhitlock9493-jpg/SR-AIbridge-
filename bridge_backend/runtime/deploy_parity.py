"""
Deploy Parity Engine — Validates runtime/build/start commands and critical environment
"""
import os
import json
import time
import pathlib
from fastapi import FastAPI
from starlette.responses import JSONResponse


_TICKETS = pathlib.Path("bridge_backend/diagnostics/stabilization_tickets")
_TICKETS.mkdir(parents=True, exist_ok=True)


async def deploy_parity_check(app: FastAPI):
    """Run deploy parity validation at startup"""
    issues = []
    
    # 1) PORT sanity
    port = os.environ.get("PORT")
    if not port:
        issues.append("PORT environment variable is missing. Render injects this at runtime.")
    else:
        try:
            int(port)
        except ValueError:
            issues.append(f"PORT value is not an integer: {port!r}")
    
    # 2) Required envs (example)
    for key in ("DATABASE_URL", "SECRET_KEY"):
        if not os.environ.get(key):
            issues.append(f"Missing required env var: {key}")
    
    # 3) Health route presence
    try:
        routes = [r.path for r in app.router.routes]
        if "/health/live" not in routes:
            issues.append("Health endpoint /health/live not registered.")
    except Exception as e:
        issues.append(f"Could not enumerate routes: {e}")
    
    if issues:
        payload = {
            "kind": "deploy-parity",
            "ts": int(time.time()),
            "issues": issues,
        }
        ticket = _TICKETS / f"{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}_deploy_parity.json"
        ticket.write_text(json.dumps(payload, indent=2))
        print(f"WARNING:deploy_parity: ⚠️  parity issues; ticket={ticket}")
    else:
        print("INFO:deploy_parity: ✅ parity OK")


async def diagnostics_parity():
    """Expose diagnostics endpoint for deploy parity tickets"""
    files = sorted(_TICKETS.glob("*_deploy_parity.json"))[-5:]
    out = []
    for f in files:
        try:
            out.append(json.loads(f.read_text()))
        except Exception:
            out.append({"file": f.name, "error": "read-failed"})
    return JSONResponse(out or [])
