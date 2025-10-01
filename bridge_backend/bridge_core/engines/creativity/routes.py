from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from .service import CreativityBay

router = APIRouter(prefix="/engines/creativity", tags=["creativity"])
C = CreativityBay()

class IngestIn(BaseModel):
    content: str
    ctype: str
    project: Optional[str] = None
    captain: Optional[str] = None
    tags: Optional[List[str]] = None

@router.post("/ingest")
def ingest(payload: IngestIn):
    return C.ingest(payload.content, payload.ctype, payload.project, payload.captain, payload.tags)

@router.get("/list")
def list_entries(limit: int = 50):
    return {"entries": C.list_entries(limit=limit)}
