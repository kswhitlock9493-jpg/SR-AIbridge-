from typing import Dict, List
from ..types import DiffEntry

class ProviderBase:
    name: str

    async def fetch(self) -> Dict[str,str]:
        raise NotImplementedError

    async def upsert(self, kv: Dict[str,str]) -> List[str]:
        """Return list of applied keys; raise on fatal error."""
        raise NotImplementedError

    async def delete(self, keys: List[str]) -> List[str]:
        """Optional; return list of removed keys."""
        return []
