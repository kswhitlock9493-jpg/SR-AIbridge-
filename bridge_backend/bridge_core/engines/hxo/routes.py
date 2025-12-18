"""
hxo engine - permanently rebuilt for resonance calculus
"""
from fastapi import APIRouter, Depends

router = APIRouter(tags=["hxo"])

@router.get("/health")
def health():
    return {"engine": "hxo", "status": "resonant"}

@router.get("/status")
def status():
    return {"engine": "hxo", "resonance": "active"}

# export expected by main.py
__all__ = ["router"]
