"""
Chimera Deployment Engine API Routes
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from pathlib import Path
import logging

from .engine import get_chimera_instance, ChimeraDeploymentEngine
from .config import ChimeraConfig

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chimera", tags=["chimera"])


class SimulateRequest(BaseModel):
    platform: str
    project_path: Optional[str] = None


class DeployRequest(BaseModel):
    platform: str
    project_path: Optional[str] = None
    auto_heal: bool = True
    certify: bool = True


@router.get("/status")
async def get_status():
    """Get Chimera engine status"""
    try:
        chimera = get_chimera_instance()
        status = await chimera.monitor()
        return status
    except Exception as e:
        logger.error(f"[Chimera API] Status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/config")
async def get_config():
    """Get Chimera configuration"""
    try:
        chimera = get_chimera_instance()
        return chimera.config.to_dict()
    except Exception as e:
        logger.error(f"[Chimera API] Config error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/simulate")
async def simulate_deployment(request: SimulateRequest):
    """
    Simulate deployment without actually deploying
    
    Runs Leviathan-powered predictive simulation
    """
    try:
        chimera = get_chimera_instance()
        
        project_path = Path(request.project_path) if request.project_path else None
        result = await chimera.simulate(request.platform, project_path)
        
        return result
    except Exception as e:
        logger.error(f"[Chimera API] Simulation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/deploy")
async def deploy(request: DeployRequest):
    """
    Execute autonomous deployment
    
    Full deployment pipeline:
    1. Predictive Simulation (Leviathan)
    2. Configuration Healing (ARIE)
    3. Truth Engine Certification
    4. Deterministic Deployment
    5. Post-Verification (Cascade)
    """
    try:
        chimera = get_chimera_instance()
        
        project_path = Path(request.project_path) if request.project_path else None
        result = await chimera.deploy(
            request.platform,
            project_path,
            request.auto_heal,
            request.certify
        )
        
        return result
    except Exception as e:
        logger.error(f"[Chimera API] Deployment error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/deployments")
async def get_deployment_history():
    """Get deployment history"""
    try:
        chimera = get_chimera_instance()
        return {
            "deployments": chimera.get_deployment_history(),
            "count": len(chimera.deployments)
        }
    except Exception as e:
        logger.error(f"[Chimera API] History error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/certifications")
async def get_certifications():
    """Get certification history"""
    try:
        chimera = get_chimera_instance()
        return {
            "certifications": chimera.certifier.get_certification_history(),
            "count": len(chimera.certifier.certifications)
        }
    except Exception as e:
        logger.error(f"[Chimera API] Certifications error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
