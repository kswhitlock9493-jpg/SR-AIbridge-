from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

try:
    from bridge_core.engines.filing import FilingEngine
except ImportError:
    from bridge_backend.bridge_core.engines.filing import FilingEngine

router = APIRouter(prefix="/engines/filing", tags=["engines"])
filing = FilingEngine()

class FileRequest(BaseModel):
    content: str
    tags: List[str]
    source: str

class SearchRequest(BaseModel):
    tag: str

class ReassembleRequest(BaseModel):
    shas: List[str]

@router.post("/file")
def file_entry(req: FileRequest):
    return filing.file_entry(req.content, req.tags, req.source)

@router.post("/search")
def search_entries(req: SearchRequest):
    return {"results": filing.search_entries(req.tag)}

@router.post("/reassemble")
def reassemble(req: ReassembleRequest):
    return {"text": filing.reassemble(req.shas)}