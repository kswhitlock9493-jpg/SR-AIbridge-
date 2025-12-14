from __future__ import annotations
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict

from .finder import find_candidates
from .binder import bind_candidates, list_truths
from .citer import cite
from .utils import TRUTH_DIR, now_iso

router = APIRouter(prefix="/engines/truth", tags=["truth"])

class FindIn(BaseModel):
    query: Optional[str] = Field(default=None, description="Optional filter substring")
    limit: int = Field(default=50, ge=1, le=500)

class BindIn(BaseModel):
    candidates: List[Dict[str, Any]]
    similarity: float = Field(default=0.72, ge=0.0, le=1.0)

class CiteIn(BaseModel):
    statement: str = Field(min_length=3)

@router.get("/status")
def status():
    return {
        "ts": now_iso(),
        "paths": {"truth_dir": str(TRUTH_DIR)},
        "ready": True
    }

@router.post("/find")
def find(payload: FindIn):
    return find_candidates(query=payload.query, limit=payload.limit)

@router.post("/bind")
def bind(payload: BindIn):
    return bind_candidates(payload.candidates, similarity=payload.similarity)

@router.post("/cite")
def do_cite(payload: CiteIn):
    return cite(payload.statement)

@router.get("/truths")
def truths(limit: int = 50):
    return list_truths(limit=limit)
