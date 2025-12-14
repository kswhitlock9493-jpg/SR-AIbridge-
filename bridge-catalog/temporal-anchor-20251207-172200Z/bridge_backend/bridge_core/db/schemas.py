from pydantic import BaseModel
from typing import Optional

class MissionSchema(BaseModel):
    id: Optional[int]
    name: str
    status: str
    created_at: str

class LogSchema(BaseModel):
    id: Optional[int]
    timestamp: str
    source: str
    message: str
    details: str = "{}"
