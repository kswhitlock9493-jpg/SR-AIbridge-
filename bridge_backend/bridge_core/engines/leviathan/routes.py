from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import List, Optional
from .service import LeviathanEngine

router = APIRouter(prefix="/engines/leviathan", tags=["leviathan"])
L = LeviathanEngine()

class SearchIn(BaseModel):
    query: str = Field(min_length=1)
    tags: Optional[List[str]] = None
    limit: int = 50
    planes: Optional[List[str]] = None  # ["creativity","parser","truth"]

@router.post("/search")
def search(payload: SearchIn):
    rows = L.search(
        query=payload.query,
        tags=payload.tags,
        limit=payload.limit,
        planes=payload.planes
    )
    return {"results": rows}
