from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from .service import CreativityBay

router = APIRouter(prefix="/engines/creativity", tags=["creativity"])
BAY = CreativityBay()

class IngestIn(BaseModel):
    title: str
    text: str
    tags: Optional[List[str]] = []
    source: str

@router.post("/ingest")
def ingest(payload: IngestIn):
    asset = BAY.ingest(payload.title, payload.text, payload.tags, payload.source)
    return {"ok": True, "asset": asset.to_dict()}

class SearchIn(BaseModel):
    query: str
    tags: Optional[List[str]] = None

@router.post("/search")
def search(payload: SearchIn):
    results = BAY.search(payload.query, payload.tags)
    return {"results": results}

@router.get("/list")
def list_entries(limit: int = 50):
    return {"entries": BAY.list_entries(limit=limit)}
