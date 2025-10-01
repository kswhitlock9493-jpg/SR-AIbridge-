from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from .service import LeviathanEngine
from datetime import datetime
import json

router = APIRouter(prefix="/engines/leviathan", tags=["leviathan"])
L = LeviathanEngine()

class IndexIn(BaseModel):
    text: str
    namespace: str
    source: str

class SearchIn(BaseModel):
    query: str
    namespaces: Optional[List[str]] = None
    limit: int = 20

@router.post("/index")
def index(payload: IndexIn):
    return L.index(payload.text, payload.namespace, payload.source)

@router.post("/search")
def search(payload: SearchIn):
    return {"results": L.search(payload.query, namespaces=payload.namespaces,
                                limit=payload.limit)}

@router.get("/sources")
def sources():
    return {"sources": L.sources()}

@router.get("/status")
def status():
    return {"status": "ok", "time": datetime.utcnow().isoformat() + "Z"}

# Stub for outward web search (extend later)
@router.get("/web")
def web_search(q: str = Query(...)):
    # in real use, call web.search() here
    dummy = {"url": "https://example.com", "title": "Example", "snippet": f"Result for {q}"}
    ts = datetime.utcnow().isoformat() + "Z"
    return {"query": q, "results": [dummy], "ts": ts}
