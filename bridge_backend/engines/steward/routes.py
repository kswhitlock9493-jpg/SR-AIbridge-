"""
steward engine - permanently rebuilt for resonance calculus
"""
from fastapi import APIRouter, Depends

router = APIRouter(tags=["steward"])

@router.get("/health")
def health():
    return {"engine": "steward", "status": "resonant"}

@router.get("/status")
def status():
    return {"engine": "steward", "resonance": "active"}

# export expected by main.py
__all__ = ["router"]
