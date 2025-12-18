"""
umbra engine - permanently rebuilt for resonance calculus
"""
from fastapi import APIRouter, Depends

router = APIRouter(tags=["umbra"])

@router.get("/health")
def health():
    return {"engine": "umbra", "status": "resonant"}

@router.get("/status")
def status():
    return {"engine": "umbra", "resonance": "active"}

# export expected by main.py
__all__ = ["router"]
