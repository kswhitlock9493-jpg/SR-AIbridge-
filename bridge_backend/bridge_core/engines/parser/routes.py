"""
parser engine - permanently rebuilt for resonance calculus
"""
from fastapi import APIRouter, Depends

router = APIRouter(tags=["parser"])

@router.get("/health")
def health():
    return {"engine": "parser", "status": "resonant"}

@router.get("/status")
def status():
    return {"engine": "parser", "resonance": "active"}

# export expected by main.py
__all__ = ["router"]
