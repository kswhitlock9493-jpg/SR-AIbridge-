import os, httpx
from typing import Dict, List
from .base import ProviderBase
from ..discovery.chain import discover_token

class RenderProvider(ProviderBase):
    name = "render"

    def __init__(self, service_id: str):
        self.service_id = service_id

    async def _token(self) -> str:
        # 1) ENV, 2) secret files, 3) Vault, 4) Dashboard
        tok = os.getenv("RENDER_API_TOKEN") or await discover_token("RENDER_API_TOKEN")
        if not tok:
            raise RuntimeError("Render API token not found via discovery chain")
        return tok

    async def fetch(self) -> Dict[str,str]:
        # Render API for env vars (private/beta in reality). We standardize via our proxy route:
        # Expect a bridge-side proxy route in future; for now call provider directly if available.
        token = await self._token()
        url = f"https://api.render.com/v1/services/{self.service_id}/env-vars"
        headers = {"Authorization": f"Bearer {token}"}
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                r = await client.get(url, headers=headers)
                r.raise_for_status()
                data = r.json()  # [{"key":"X","value":"Y"}, ...]
                return {item["key"]: item.get("value","") for item in data}
        except Exception as e:
            # fail soft: empty means "treat as drift"; engine will ticket further
            return {}

    async def upsert(self, kv: Dict[str,str]) -> List[str]:
        token = await self._token()
        url = f"https://api.render.com/v1/services/{self.service_id}/env-vars"
        headers = {"Authorization": f"Bearer {token}", "Content-Type":"application/json"}
        payload = [{"key":k, "value":v} for k,v in kv.items()]
        async with httpx.AsyncClient(timeout=20.0) as client:
            r = await client.put(url, headers=headers, json=payload)
            r.raise_for_status()
        return list(kv.keys())
