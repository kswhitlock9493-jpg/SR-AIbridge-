"""
Chimera API Routes
Predictive deployment and preflight validation
"""

from fastapi import APIRouter, HTTPException
from pathlib import Path
from typing import Dict, Any
import logging

from .core import ChimeraEngine, ChimeraOracle

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chimera", tags=["chimera"])


@router.post("/preflight")
async def chimera_preflight():
    """Run Chimera preflight validation (legacy)"""
    eng = ChimeraEngine(Path(".").resolve())
    return await eng.preflight()


@router.post("/deploy/predictive")
async def predictive_deploy(payload: Dict[str, Any]):
    """
    Execute predictive deployment pipeline
    
    **RBAC**: Admiral
    
    Body:
        {
            "ref": "commit-sha or branch"
        }
    """
    try:
        oracle = ChimeraOracle()
        result = await oracle.run(payload)
        return {
            "status": "success",
            "result": result
        }
    except Exception as e:
        logger.error(f"Predictive deploy failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health():
    """Health check endpoint"""
    return {"engine": "chimera-oracle", "status": "ok", "version": "1.9.7i"}
