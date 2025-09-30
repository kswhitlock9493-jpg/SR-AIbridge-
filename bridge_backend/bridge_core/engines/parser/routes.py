from fastapi import APIRouter, HTTPException, Body, Query
from pydantic import BaseModel
from typing import List, Optional
from .service import ParserEngine

router = APIRouter(prefix="/engines/parser", tags=["parser"])
P = ParserEngine()

# ---- already present in 5b (kept) ----
class IngestIn(BaseModel):
    raw: str
    source: Optional[str] = None
    max_chunk: int = 2000

@router.post("/ingest")
def ingest(payload: IngestIn):
    r = P.ingest(payload.raw, source=payload.source, max_chunk=payload.max_chunk)
    return {"ok": r.ok, "seen": r.seen, "filed": r.filed, "manifest": r.manifest}

class ReassembleIn(BaseModel):
    sha_list: List[str]

@router.post("/reassemble")
def reassemble(payload: ReassembleIn):
    try:
        text = P.reassemble(payload.sha_list)
        return {"text": text}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

# ---- NEW in 5c ----
class TagIn(BaseModel):
    sha: str
    tags: List[str]

@router.post("/tag/add")
def tag_add(payload: TagIn):
    try:
        return P.add_tags(payload.sha, payload.tags)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="chunk_not_found")

@router.post("/tag/remove")
def tag_remove(payload: TagIn):
    try:
        return P.remove_tags(payload.sha, payload.tags)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="chunk_not_found")

class LinkIn(BaseModel):
    parent_sha: str
    child_sha: str
    relation: Optional[str] = "derives"

@router.post("/link")
def link(payload: LinkIn):
    try:
        return P.link(payload.parent_sha, payload.child_sha, payload.relation or "derives")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="chunk_not_found")

@router.get("/chunk/{sha}")
def chunk_manifest(sha: str):
    try:
        return P.manifest(sha)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="chunk_not_found")

@router.get("/list")
def list_chunks(tag: Optional[str] = None, source: Optional[str] = None, limit: int = 100):
    return P.list(tag=tag, source=source, limit=limit)

@router.get("/search")
def search(q: str = Query(..., min_length=2), limit: int = 50):
    return P.search(q, limit=limit)