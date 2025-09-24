"""
Guardian status and monitoring endpoints for SR-AIbridge
Alternative guardian endpoint organization
"""
from fastapi import APIRouter, HTTPException
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["guardian-status"])

@router.get("/guardian/status")
async def get_guardian_status():
    """Get Guardian daemon status for frontend polling"""
    from ..main import guardian
    return guardian.get_status()

@router.post("/guardian/selftest")
async def run_guardian_selftest():
    """Manually trigger Guardian self-test"""
    from ..main import guardian
    
    try:
        await guardian.run_selftest()
        return {
            "success": True,
            "message": "Self-test completed", 
            "status": guardian.selftest_status,
            "last_selftest": guardian.last_selftest.isoformat() if guardian.last_selftest else None
        }
    except Exception as e:
        logger.error(f"Guardian selftest endpoint error: {e}")
        raise HTTPException(status_code=500, detail=f"Self-test failed: {str(e)}")

@router.post("/guardian/activate")
async def activate_guardian():
    """Manually activate Guardian daemon"""
    from ..main import guardian
    
    try:
        result = await guardian.activate()
        return result
    except Exception as e:
        logger.error(f"Guardian activation error: {e}")
        raise HTTPException(status_code=500, detail=f"Activation failed: {str(e)}")