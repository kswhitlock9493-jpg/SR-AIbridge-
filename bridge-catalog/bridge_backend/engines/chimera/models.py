"""
Chimera Engine Models
"""

from typing import Optional, Dict
from pydantic import BaseModel


class RedirectRule(BaseModel):
    """Netlify redirect rule model"""
    from_path: str
    to_path: str
    status: int = 200
    force: bool = False
    conditions: Optional[Dict[str, str]] = None
