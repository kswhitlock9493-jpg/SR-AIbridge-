"""
Hydra Guard API Routes
RESTful endpoints for Netlify configuration synthesis
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging

from .guard import HydraGuard

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/hydra", tags=["hydra"])


@router.post("/synthesize")
async def synthesize_config():
    """
    Synthesize and validate Netlify configuration
    
    **RBAC**: Admiral, Captain
    """
    try:
        guard = HydraGuard()
        result = await guard.synthesize_and_validate()
        return {
            "status": "success",
            "result": result
        }
    except Exception as e:
        logger.error(f"Hydra synthesis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health():
    """Health check endpoint"""
    return {"engine": "hydra-guard", "status": "ok", "version": "2.0"}
