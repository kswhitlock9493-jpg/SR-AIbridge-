"""
EnvScribe API Routes
Provides REST endpoints for environment intelligence system
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging

from .core import EnvScribeEngine
from .emitters import EnvScribeEmitter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/envscribe", tags=["envscribe"])


@router.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "engine": "EnvScribe v1.9.6u",
        "features": ["scan", "verify", "emit", "genesis_integration"]
    }


@router.get("/report")
async def get_report():
    """
    Get the current EnvScribe scan report.
    Returns the latest environment intelligence data.
    """
    engine = EnvScribeEngine()
    report = engine.load_report()
    
    if not report:
        raise HTTPException(
            status_code=404, 
            detail="No report available. Run scan first."
        )
    
    return report.to_dict()


@router.post("/scan")
async def run_scan():
    """
    Perform a comprehensive environment scan.
    Scans repository, compiles variables, and verifies against platforms.
    """
    engine = EnvScribeEngine()
    
    try:
        report = await engine.scan()
        return {
            "success": True,
            "report": report.to_dict()
        }
    except Exception as e:
        logger.error(f"❌ Scan failed: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Scan failed: {str(e)}"
        )


@router.post("/emit")
async def emit_artifacts():
    """
    Generate all output artifacts from the latest scan.
    Creates ENV_OVERVIEW.md, copy blocks, and platform configs.
    """
    engine = EnvScribeEngine()
    report = engine.load_report()
    
    if not report:
        raise HTTPException(
            status_code=404,
            detail="No report available. Run scan first."
        )
    
    try:
        emitter = EnvScribeEmitter()
        outputs = emitter.emit_all(report)
        
        return {
            "success": True,
            "outputs": outputs,
            "copy_blocks": emitter.generate_copy_blocks(report)
        }
    except Exception as e:
        logger.error(f"❌ Emit failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Emit failed: {str(e)}"
        )


@router.post("/audit")
async def full_audit():
    """
    Perform full audit: scan + emit + certify.
    This is the primary endpoint for complete environment intelligence.
    """
    try:
        # Scan
        engine = EnvScribeEngine()
        report = await engine.scan()
        
        # Emit artifacts
        emitter = EnvScribeEmitter()
        outputs = emitter.emit_all(report)
        
        # Notify Genesis (if available)
        try:
            await _notify_genesis_scan_complete(report)
        except Exception as e:
            logger.debug(f"Genesis notification skipped: {e}")
        
        # Request Truth certification (if available)
        try:
            certified = await _request_truth_certification(report)
            if certified:
                report.certified = True
                report.certificate_id = certified.get("certificate_id")
                engine._save_report(report)
        except Exception as e:
            logger.debug(f"Truth certification skipped: {e}")
        
        return {
            "success": True,
            "summary": report.summary.to_dict(),
            "outputs": outputs,
            "certified": report.certified,
            "certificate_id": report.certificate_id
        }
    except Exception as e:
        logger.error(f"❌ Full audit failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Audit failed: {str(e)}"
        )


@router.get("/copy/{platform}")
async def get_copy_block(platform: str):
    """
    Get copy-ready environment block for a specific platform.
    
    Platforms: render, netlify, github_vars, github_secrets
    """
    engine = EnvScribeEngine()
    report = engine.load_report()
    
    if not report:
        raise HTTPException(
            status_code=404,
            detail="No report available. Run scan first."
        )
    
    emitter = EnvScribeEmitter()
    blocks = emitter.generate_copy_blocks(report)
    
    if platform not in blocks:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid platform. Choose from: {', '.join(blocks.keys())}"
        )
    
    return {
        "platform": platform,
        "content": blocks[platform]
    }


async def _notify_genesis_scan_complete(report: Any):
    """Notify Genesis bus that EnvScribe scan is complete"""
    try:
        from bridge_backend.genesis.bus import genesis_bus
        
        await genesis_bus.publish("genesis.echo", {
            "type": "ENVSCRIBE_SCAN_COMPLETE",
            "source": "envscribe.core",
            "total_keys": report.summary.total_keys,
            "verified": report.summary.verified,
            "missing_total": (
                report.summary.missing_in_render + 
                report.summary.missing_in_netlify + 
                report.summary.missing_in_github
            ),
            "timestamp": report.summary.timestamp
        })
        logger.info("[EnvScribe→Genesis] Scan complete notification sent")
    except ImportError:
        logger.debug("[EnvScribe→Genesis] Genesis bus not available")


async def _request_truth_certification(report: Any) -> Dict[str, Any]:
    """Request Truth Engine certification for environment configuration"""
    try:
        from bridge_backend.bridge_core.engines.truth.service import TruthEngine
        
        truth_engine = TruthEngine()
        
        # Create certification request
        cert_request = {
            "context": "envscribe_environment",
            "total_keys": report.summary.total_keys,
            "verified": report.summary.verified,
            "missing": (
                report.summary.missing_in_render + 
                report.summary.missing_in_netlify + 
                report.summary.missing_in_github
            ),
            "drifted": report.summary.drifted
        }
        
        # Request certification
        result = await truth_engine.certify(cert_request)
        
        if result.get("certified"):
            logger.info(f"[EnvScribe→Truth] Configuration certified: {result.get('certificate_id')}")
            
            # Publish certification event to Genesis
            try:
                from bridge_backend.genesis.bus import genesis_bus
                await genesis_bus.publish("genesis.echo", {
                    "type": "ENVSCRIBE_CERTIFIED",
                    "source": "truth.engine",
                    "certificate_id": result.get("certificate_id"),
                    "timestamp": report.summary.timestamp
                })
            except ImportError:
                pass
        
        return result
    except Exception as e:
        logger.debug(f"[EnvScribe→Truth] Certification request failed: {e}")
        return {"certified": False, "reason": str(e)}
