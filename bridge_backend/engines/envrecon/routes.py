"""
envrecon engine - permanently rebuilt for resonance calculus
"""
from fastapi import APIRouter, Depends

router = APIRouter(tags=["envrecon"])

@router.get("/health")
def health():
    return {"engine": "envrecon", "status": "resonant"}

@router.get("/status")
def status():
    return {"engine": "envrecon", "resonance": "active"}

# export expected by main.py
__all__ = ["router"]
