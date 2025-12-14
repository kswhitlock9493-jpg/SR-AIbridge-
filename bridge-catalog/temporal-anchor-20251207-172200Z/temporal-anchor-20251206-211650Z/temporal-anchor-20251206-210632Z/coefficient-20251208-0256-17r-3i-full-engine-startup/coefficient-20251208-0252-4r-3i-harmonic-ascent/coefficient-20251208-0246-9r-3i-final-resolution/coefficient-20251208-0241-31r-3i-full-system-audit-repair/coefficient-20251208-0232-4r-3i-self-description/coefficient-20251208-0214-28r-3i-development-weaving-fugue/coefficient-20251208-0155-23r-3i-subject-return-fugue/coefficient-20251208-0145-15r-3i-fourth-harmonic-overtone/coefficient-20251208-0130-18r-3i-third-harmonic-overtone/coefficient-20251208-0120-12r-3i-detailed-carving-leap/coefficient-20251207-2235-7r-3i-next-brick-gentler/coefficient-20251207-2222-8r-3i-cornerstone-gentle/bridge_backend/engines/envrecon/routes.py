"""
EnvRecon API Routes
Provides REST endpoints for environment reconciliation and synchronization
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
import logging

from .core import EnvReconEngine
from .hubsync import hubsync
from .autoheal import autoheal

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/envrecon", tags=["envrecon"])


@router.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "engine": "EnvRecon v2.0.2",
        "features": ["reconciliation", "hubsync", "autoheal", "inspector"]
    }


@router.get("/report")
async def get_report():
    """
    Get the current environment reconciliation report.
    Returns the latest JSON diff.
    """
    engine = EnvReconEngine()
    report = engine.load_report()
    
    if not report:
        raise HTTPException(status_code=404, detail="No report available. Run audit first.")
    
    return report


@router.post("/audit")
async def run_audit():
    """
    Perform a full environment audit across all platforms.
    Generates a new reconciliation report.
    """
    engine = EnvReconEngine()
    
    try:
        report = await engine.reconcile()
        return {
            "success": True,
            "report": report
        }
    except Exception as e:
        logger.error(f"❌ Audit failed: {e}")
        raise HTTPException(status_code=500, detail=f"Audit failed: {str(e)}")


@router.post("/sync")
async def sync_all():
    """
    Auto-sync all platforms.
    This endpoint triggers synchronization across Render, Netlify, and GitHub.
    """
    engine = EnvReconEngine()
    
    try:
        # First, run audit
        report = await engine.reconcile()
        
        # Attempt auto-heal
        heal_result = await autoheal.heal_environment(report)
        
        # Update report with auto-fixed items
        report["autofixed"] = heal_result.get("healed", [])
        engine.save_report(report)
        
        # Notify Autonomy engine of heal completion
        try:
            from bridge_backend.bridge_core.engines.adapters.envrecon_autonomy_link import envrecon_autonomy_link
            await envrecon_autonomy_link.notify_heal_complete(heal_result, report)
        except Exception as e:
            logger.debug(f"EnvRecon-Autonomy heal notification skipped: {e}")
        
        return {
            "success": True,
            "report": report,
            "heal_summary": heal_result
        }
    except Exception as e:
        logger.error(f"❌ Sync failed: {e}")
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")


@router.post("/sync/github")
async def sync_github_secrets(secrets: List[Dict[str, str]]):
    """
    Sync specific secrets to GitHub.
    
    Request body: [{"name": "SECRET_NAME", "value": "secret_value"}, ...]
    """
    if not hubsync.is_configured():
        raise HTTPException(
            status_code=400,
            detail="HubSync not configured. Set GITHUB_TOKEN and GITHUB_REPO."
        )
    
    try:
        result = await hubsync.autofix_github_secrets(secrets)
        return result
    except Exception as e:
        logger.error(f"❌ GitHub sync failed: {e}")
        raise HTTPException(status_code=500, detail=f"GitHub sync failed: {str(e)}")


@router.post("/heal")
async def trigger_heal():
    """
    Manually trigger auto-healing based on the latest report.
    """
    engine = EnvReconEngine()
    report = engine.load_report()
    
    if not report:
        raise HTTPException(status_code=404, detail="No report available. Run audit first.")
    
    try:
        heal_result = await autoheal.heal_environment(report)
        
        # Update report with healed items
        report["autofixed"] = heal_result.get("healed", [])
        engine.save_report(report)
        
        return {
            "success": True,
            "heal_summary": heal_result
        }
    except Exception as e:
        logger.error(f"❌ Healing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Healing failed: {str(e)}")
