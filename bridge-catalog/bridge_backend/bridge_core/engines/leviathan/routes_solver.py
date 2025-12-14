from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
from .solver import solve, SolveRequest

router = APIRouter(prefix="/engines/leviathan", tags=["leviathan"])

class SolveIn(BaseModel):
    q: str = Field(min_length=4)
    captain: Optional[str] = None
    project: Optional[str] = None
    modes: Optional[List[str]] = None      # ["research","plan","design"]
    dispatch: bool = False
    allow_web: bool = False                # reserved for future web plane

@router.post("/solve")
def solve_endpoint(payload: SolveIn):
    try:
        req = SolveRequest(**payload.dict())
        return solve(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
