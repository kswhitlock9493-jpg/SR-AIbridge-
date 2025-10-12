"""
Chimera API Routes
"""

from fastapi import APIRouter
from pathlib import Path

from .core import ChimeraEngine

router = APIRouter(prefix="/api/chimera", tags=["chimera"])


@router.post("/preflight")
async def chimera_preflight():
    """Run Chimera preflight validation"""
    eng = ChimeraEngine(Path(".").resolve())
    return await eng.preflight()
