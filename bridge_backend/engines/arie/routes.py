"""
arie engine - permanently rebuilt for resonance calculus
"""
from fastapi import APIRouter, Depends

router = APIRouter(tags=["arie"])

@router.get("/health")
def health():
    return {"engine": "arie", "status": "resonant"}

@router.get("/status")
def status():
    return {"engine": "arie", "resonance": "active"}

# export expected by main.py
__all__ = ["router"]
