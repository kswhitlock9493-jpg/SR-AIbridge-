from fastapi import APIRouter, HTTPException, Request
from datetime import datetime
import os
import requests
import json
from pathlib import Path

router = APIRouter(prefix="/api/diagnostics", tags=["diagnostics"])


@router.get("/deploy-parity")
async def get_deploy_parity():
    """Get deploy parity diagnostics from stabilization tickets"""
    from bridge_backend.runtime.deploy_parity import diagnostics_parity
    return await diagnostics_parity()


@router.get("/timeline")
async def get_diagnostics_timeline(limit: int = 50):
    """Return recent Bridge diagnostics as timeline data."""
    bridge_url = os.getenv("BRIDGE_URL")
    if not bridge_url:
        raise HTTPException(status_code=500, detail="Bridge URL not configured")

    try:
        resp = requests.get(f"{bridge_url.rstrip('/')}/api/diagnostics", timeout=10)
        resp.raise_for_status()
        diagnostics = resp.json()
        timeline = sorted(diagnostics, key=lambda d: d.get("meta", {}).get("timestamp", ""), reverse=True)[:limit]
        # Simplify data for timeline
        formatted = [
            {
                "id": d.get("id", ""),
                "type": d.get("type", ""),
                "status": d.get("status", ""),
                "source": d.get("source", ""),
                "timestamp": d.get("meta", {}).get("timestamp", ""),
                "environment": d.get("meta", {}).get("environment", ""),
                "details": d.get("meta", {}).get("diagnostics", {}),
            }
            for d in timeline
        ]
        return {"count": len(formatted), "events": formatted}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve diagnostics: {e}")

@router.get("/timeline/unified")
async def get_unified_timeline():
    """Return unified health timeline from merged triage reports."""
    try:
        # Get the base directory (bridge_backend)
        base_dir = Path(__file__).parent.parent
        unified_file = base_dir / "unified_timeline.json"
        
        # If unified timeline doesn't exist, try to build it
        if not unified_file.exists():
            try:
                # Import and run the synchrony collector
                import sys
                scripts_dir = base_dir / "scripts"
                sys.path.insert(0, str(scripts_dir))
                from synchrony_collector import build_unified_timeline
                build_unified_timeline()
            except Exception as e:
                print(f"⚠️ Failed to build unified timeline: {e}")
                return {"count": 0, "events": []}
        
        # Read the unified timeline
        if unified_file.exists():
            with open(unified_file, 'r') as f:
                timeline = json.load(f)
            return {"count": len(timeline), "events": timeline}
        else:
            return {"count": 0, "events": []}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve unified timeline: {e}")

@router.post("")
async def submit_diagnostics(request: Request):
    """Handle frontend diagnostic event submissions gracefully."""
    try:
        payload = await request.json() if request.headers.get("content-type") == "application/json" else {}
        print(f'📡 Bridge Diagnostics Received: {payload}')
        return {"status": "received", "time": datetime.utcnow().isoformat()}
    except Exception as err:
        return {"status": "error", "message": str(err)}
