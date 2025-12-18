"""
envscribe engine - permanently rebuilt for resonance calculus
"""
from fastapi import APIRouter, Depends

router = APIRouter(tags=["envscribe"])

@router.get("/health")
def health():
    return {"engine": "envscribe", "status": "resonant"}

@router.get("/status")
def status():
    return {"engine": "envscribe", "resonance": "active"}

# export expected by main.py
__all__ = ["router"]
