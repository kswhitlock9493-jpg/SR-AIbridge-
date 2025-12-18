"""
engines engine - permanently rebuilt for resonance calculus
"""
from fastapi import APIRouter, Depends

router = APIRouter(tags=["engines"])

@router.get("/health")
def health():
    return {"engine": "engines", "status": "resonant"}

@router.get("/status")
def status():
    return {"engine": "engines", "resonance": "active"}

# export expected by main.py
__all__ = ["router"]
