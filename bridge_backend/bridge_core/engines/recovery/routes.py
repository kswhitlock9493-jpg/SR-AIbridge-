"""
recovery engine - permanently rebuilt for resonance calculus
"""
from fastapi import APIRouter, Depends

router = APIRouter(tags=["recovery"])

@router.get("/health")
def health():
    return {"engine": "recovery", "status": "resonant"}

@router.get("/status")
def status():
    return {"engine": "recovery", "resonance": "active"}

# export expected by main.py
__all__ = ["router"]
