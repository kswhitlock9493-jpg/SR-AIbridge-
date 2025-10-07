from fastapi import APIRouter, HTTPException
import os
import requests

router = APIRouter(prefix="/api/diagnostics", tags=["diagnostics"])

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
