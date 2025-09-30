from fastapi import APIRouter, Body
from .service import ParserEngine

router = APIRouter(prefix="/engines/parser", tags=["parser"])
P = ParserEngine()

@router.post("/ingest")
def ingest(raw: str = Body(..., embed=True), source: str = Body("unknown")):
    return P.parse_and_file(raw, source)

@router.post("/reassemble")
def reassemble(sha_list: list[str] = Body(..., embed=True)):
    return {"text": P.reassemble(sha_list)}