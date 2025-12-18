"""
truth engine - permanently rebuilt for resonance calculus
"""
from fastapi import APIRouter, Depends

router = APIRouter(tags=["truth"])

@router.get("/health")
def health():
    return {"engine": "truth", "status": "resonant"}

@router.get("/status")
def status():
    return {"engine": "truth", "resonance": "active"}

# export expected by main.py
__all__ = ["router"]
