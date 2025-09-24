"""
Guardian daemon endpoints for SR-AIbridge
Handles guardian daemon status, self-test, and activation
"""
from fastapi import APIRouter, HTTPException, Depends
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/guardian", tags=["guardian"])

def get_guardian():
    """Dependency to get guardian instance"""
    # This will be properly injected when the router is included
    from ..main import guardian
    return guardian

@router.get("/status")
async def get_guardian_status(guardian_service = Depends(get_guardian)):
    """Get Guardian daemon status for frontend polling"""
    return guardian_service.get_status()

@router.post("/selftest")
async def run_guardian_selftest(guardian_service = Depends(get_guardian)):
    """Manually trigger Guardian self-test"""
    try:
        await guardian_service.run_selftest()
        return {
            "success": True,
            "message": "Self-test completed",
            "status": guardian_service.selftest_status,
            "last_selftest": guardian_service.last_selftest.isoformat() if guardian_service.last_selftest else None
        }
    except Exception as e:
        logger.error(f"Guardian selftest endpoint error: {e}")
        raise HTTPException(status_code=500, detail=f"Self-test failed: {str(e)}")

@router.post("/activate")
async def activate_guardian(guardian_service = Depends(get_guardian)):
    """Manually activate Guardian daemon"""
    try:
        result = await guardian_service.activate()
        return result
    except Exception as e:
        logger.error(f"Guardian activation error: {e}")
        raise HTTPException(status_code=500, detail=f"Activation failed: {str(e)}")