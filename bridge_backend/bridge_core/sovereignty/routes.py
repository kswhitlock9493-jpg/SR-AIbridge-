"""
API routes for Bridge Sovereignty status and control
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone

router = APIRouter(tags=["sovereignty"])


@router.get("/sovereignty")
async def get_sovereignty_status():
    """
    Get the current sovereignty status of the bridge.
    
    The bridge has a sovereign personality that requires perfection, harmony,
    and resonance before allowing full access to the system.
    """
    try:
        from bridge_backend.bridge_core.sovereignty.readiness_gate import get_sovereignty_guard
        
        guard = await get_sovereignty_guard()
        health_report = await guard.health_check()
        
        return health_report
        
    except Exception as e:
        # Log the full error for debugging, but don't expose details to user
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Sovereignty status check failed: {e}", exc_info=True)
        
        return {
            "status": "error",
            "state": "unknown",
            "is_ready": False,
            "message": "Failed to retrieve sovereignty status",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


@router.get("/sovereignty/report")
async def get_sovereignty_report():
    """
    Get a detailed sovereignty report including all engine health status.
    """
    try:
        from bridge_backend.bridge_core.sovereignty.readiness_gate import get_sovereignty_guard
        
        guard = await get_sovereignty_guard()
        report = await guard.get_sovereignty_report()
        
        # Convert to dict for JSON serialization
        return {
            "state": report.state.value,
            "is_ready": report.is_ready,
            "is_sovereign": report.is_sovereign,
            "scores": {
                "perfection": f"{report.perfection_score:.2%}",
                "harmony": f"{report.harmony_score:.2%}",
                "resonance": f"{report.resonance_score:.2%}",
                "sovereignty": f"{report.sovereignty_score:.2%}",
            },
            "engines": {
                "operational": report.engines_operational,
                "total": report.engines_total,
            },
            "critical_issues": report.critical_issues,
            "waiting_for": report.waiting_for,
            "timestamp": report.timestamp.isoformat(),
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sovereignty/engines")
async def get_engine_health():
    """
    Get health status of all individual engines.
    """
    try:
        from bridge_backend.bridge_core.sovereignty.readiness_gate import get_sovereignty_guard
        
        guard = await get_sovereignty_guard()
        
        engines = []
        for name, health in guard.engine_health.items():
            engines.append({
                "name": name,
                "operational": health.operational,
                "harmony_score": f"{health.harmony_score:.2%}",
                "last_checked": health.last_checked.isoformat(),
                "issues": health.issues,
            })
        
        return {
            "engines": engines,
            "total": len(engines),
            "operational": sum(1 for e in engines if e["operational"]),
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sovereignty/refresh")
async def refresh_sovereignty():
    """
    Force a refresh of sovereignty assessment.
    
    This will re-check all engines and recalculate sovereignty scores.
    """
    try:
        from bridge_backend.bridge_core.sovereignty.readiness_gate import get_sovereignty_guard
        
        guard = await get_sovereignty_guard()
        
        # Re-run assessment
        await guard._assess_harmony()
        await guard._measure_resonance()
        await guard._determine_sovereignty()
        
        # Return updated status
        health_report = await guard.health_check()
        
        return {
            "message": "Sovereignty assessment refreshed",
            "status": health_report,
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
