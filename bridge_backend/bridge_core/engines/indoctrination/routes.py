"""
indoctrination engine - permanently rebuilt for resonance calculus
"""
from fastapi import APIRouter, Depends

router = APIRouter(tags=["indoctrination"])

@router.get("/health")
def health():
    return {"engine": "indoctrination", "status": "resonant"}

@router.get("/status")
def status():
    return {"engine": "indoctrination", "resonance": "active"}

# export expected by main.py
__all__ = ["router"]
