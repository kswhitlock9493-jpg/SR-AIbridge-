from fastapi import APIRouter, Request, HTTPException
import os
import requests
import hmac
import hashlib
import subprocess
import sys
import json
import time
import gzip
from datetime import datetime
from pathlib import Path

router = APIRouter(prefix="/api/control", tags=["control"])

# Stabilization tickets directory
TICKETS = Path("bridge_backend/diagnostics/stabilization_tickets")
TICKETS.mkdir(parents=True, exist_ok=True)

def verify_signature(request: Request):
    """Verify Bridge control requests using HMAC secret"""
    secret = os.getenv("BRIDGE_CONTROL_SECRET")
    signature = request.headers.get("X-Bridge-Signature")
    if not secret or not signature:
        return False
    body = request._body.decode("utf-8") if hasattr(request, "_body") else ""
    computed = hmac.new(secret.encode(), body.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(computed, signature)

@router.post("/rollback")
async def trigger_rollback(request: Request):
    """Bridge-controlled rollback trigger"""
    if not verify_signature(request):
        raise HTTPException(status_code=401, detail="Invalid signature")

    token = os.getenv("NETLIFY_AUTH_TOKEN")
    site_id = os.getenv("NETLIFY_SITE_ID")
    webhook = os.getenv("BRIDGE_SLACK_WEBHOOK")
    bridge_url = os.getenv("BRIDGE_URL")

    if not token or not site_id:
        raise HTTPException(status_code=500, detail="Missing Netlify credentials")

    headers = {"Authorization": f"Bearer {token}"}
    list_url = f"https://api.netlify.com/api/v1/sites/{site_id}/deploys"
    try:
        r = requests.get(list_url, headers=headers, timeout=10)
        r.raise_for_status()
        deploys = r.json()
        last_success = next((d for d in deploys if d["state"] == "ready"), None)
        if not last_success:
            raise HTTPException(status_code=404, detail="No successful deploys found")

        restore_url = f"https://api.netlify.com/api/v1/sites/{site_id}/deploys/{last_success['id']}/restore"
        res = requests.post(restore_url, headers=headers, timeout=10)
        if res.status_code != 200:
            raise HTTPException(status_code=500, detail=f"Rollback failed: {res.text}")

        # log to diagnostics
        diag_payload = {
            "type": "DEPLOYMENT_ROLLBACK",
            "status": "success",
            "source": "BridgeControl",
            "meta": {
                "environment": "Netlify",
                "trigger": "Manual",
                "timestamp": datetime.utcnow().isoformat()+"Z",
                "diagnostics": {"rollback_id": last_success["id"]}
            }
        }
        if bridge_url:
            requests.post(f"{bridge_url.rstrip('/')}/api/diagnostics", json=diag_payload, timeout=10)

        # Slack notify
        if webhook:
            requests.post(webhook, json={"text": f"♻️ Manual rollback triggered from Bridge Dashboard. Restored deploy `{last_success['id']}`"}, timeout=5)

        return {"message": "Rollback successful", "rollback_id": last_success["id"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/hooks/triage")
async def trigger_hooks_triage(request: Request):
    """
    Manually trigger hooks triage
    Requires HMAC signature validation
    """
    if not verify_signature(request):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    # Run hooks triage script
    try:
        script_path = Path(__file__).parent.parent / "scripts" / "hooks_triage.py"
        
        if not script_path.exists():
            raise HTTPException(status_code=500, detail="Hooks triage script not found")
        
        # Run in background
        subprocess.Popen(
            [sys.executable, str(script_path), "--manual"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        return {"message": "Hooks triage initiated", "status": "running"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to run hooks triage: {str(e)}")


@router.get("/render-ok", response_model=None)
def render_ok():
    """Render health check endpoint"""
    return {"ok": True}


@router.get("/health", response_model=None)
@router.post("/health", response_model=None)
def health():
    """Basic health check endpoint - supports GET and POST for compatibility"""
    return {"status": "ok"}


@router.post("/incidents/replay/{ticket_id}")
async def replay_incident(ticket_id: str):
    """Replay a specific incident from stabilization tickets"""
    path = TICKETS / ticket_id
    if not path.exists():
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    try:
        data = json.loads(path.read_text())
        # Log the replay attempt
        print(f"INFO:control: Replaying incident ticket {ticket_id}")
        return {"status": "replayed", "ticket": ticket_id, "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to replay incident: {str(e)}")


def sweep_old_tickets(hours=72):
    """Sweep and compress old stabilization tickets"""
    cutoff = time.time() - hours * 3600
    compressed = 0
    for f in TICKETS.glob("*.json"):
        if f.stat().st_mtime < cutoff:
            gz = f.with_suffix(".json.gz")
            with gzip.open(gz, "wb") as z:
                z.write(f.read_bytes())
            f.unlink(missing_ok=True)
            compressed += 1
    return compressed

