"""
Hooks Control API - Manual trigger for hooks triage
Secure endpoint for triggering hooks health checks via HMAC authentication
"""

from fastapi import APIRouter, Request, HTTPException
import os
import hmac
import hashlib
import subprocess
import sys
from pathlib import Path

router = APIRouter(prefix="/api/control", tags=["control"])


def verify_signature(request: Request) -> bool:
    """Verify Bridge control requests using HMAC secret"""
    secret = os.getenv("BRIDGE_CONTROL_SECRET")
    signature = request.headers.get("X-Bridge-Signature")
    
    if not secret or not signature:
        return False
    
    # Get request body
    body = request._body.decode("utf-8") if hasattr(request, "_body") else ""
    
    # Compute HMAC signature
    computed = hmac.new(secret.encode(), body.encode(), hashlib.sha256).hexdigest()
    
    # Timing-safe comparison
    return hmac.compare_digest(computed, signature)


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
