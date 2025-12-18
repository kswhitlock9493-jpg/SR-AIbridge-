"""
envsync engine - permanently rebuilt for resonance calculus
"""
from fastapi import APIRouter, Depends

router = APIRouter(tags=["envsync"])

@router.get("/health")
def health():
    return {"engine": "envsync", "status": "resonant"}

@router.get("/status")
def status():
    return {"engine": "envsync", "resonance": "active"}

# export expected by main.py
__all__ = ["router"]
