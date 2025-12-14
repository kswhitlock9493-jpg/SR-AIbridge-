from fastapi import APIRouter
from typing import Dict
from .engine import sync_provider
from .config import CONFIG

router = APIRouter(prefix="/envsync", tags=["envsync"])

@router.get("/health")
async def health():
    return {"enabled": CONFIG.enabled, "mode": CONFIG.mode, "targets": CONFIG.targets}

@router.post("/dry-run/{provider}")
async def dry_run(provider: str):
    return await sync_provider(provider, mode="dry-run")

@router.post("/apply/{provider}")
async def apply(provider: str):
    return await sync_provider(provider, mode="enforce")

@router.post("/apply-all")
async def apply_all():
    out = {}
    for p in CONFIG.targets:
        out[p] = await sync_provider(p, mode="enforce")
    return out
