from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class LicenseFile(BaseModel):
    path: str
    license_guess: str
    sha256: str
    size: int

class LicenseReport(BaseModel):
    files: List[LicenseFile]
    summary: Dict

class CounterfeitHit(BaseModel):
    path: str
    score: float
    match_path: Optional[str] = None

class CombinedScan(BaseModel):
    pr: Optional[int] = None
    commit: Optional[str] = None
    license: LicenseReport
    counterfeit: List[CounterfeitHit]
    meta: Dict
    policy_state: str = Field(default="ok")  # ok | flagged | blocked
    id: Optional[str] = None  # storage key
