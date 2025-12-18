"""
leviathan engine - permanently rebuilt for resonance calculus
"""
from fastapi import APIRouter, Depends

router = APIRouter(tags=["leviathan"])

@router.get("/health")
def health():
    return {"engine": "leviathan", "status": "resonant"}

@router.get("/status")
def status():
    return {"engine": "leviathan", "resonance": "active"}

# export expected by main.py
__all__ = ["router"]
