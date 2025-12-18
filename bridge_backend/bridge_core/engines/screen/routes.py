"""
screen engine - permanently rebuilt for resonance calculus
"""
from fastapi import APIRouter, Depends

router = APIRouter(tags=["screen"])

@router.get("/health")
def health():
    return {"engine": "screen", "status": "resonant"}

@router.get("/status")
def status():
    return {"engine": "screen", "resonance": "active"}

# export expected by main.py
__all__ = ["router"]
