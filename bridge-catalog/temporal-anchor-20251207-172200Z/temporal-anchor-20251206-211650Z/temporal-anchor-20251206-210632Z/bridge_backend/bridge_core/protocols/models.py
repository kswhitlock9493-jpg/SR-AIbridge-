from pydantic import BaseModel
from typing import List, Optional


class Protocol(BaseModel):
    """Schema for a single protocol."""
    name: str
    status: str
    details: Optional[str] = None


class ProtocolList(BaseModel):
    """Schema for a list of protocols."""
    protocols: List[Protocol]