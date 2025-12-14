import os, httpx
from typing import Dict, List
from .base import ProviderBase
from ..discovery.chain import discover_token

class NetlifyProvider(ProviderBase):
    name = "netlify"

    def __init__(self, site_id: str):
        self.site_id = site_id

    async def _token(self) -> str:
        tok = os.getenv("NETLIFY_API_TOKEN") or await discover_token("NETLIFY_API_TOKEN")
        if not tok:
            raise RuntimeError("Netlify API token not found via discovery chain")
        return tok

    async def fetch(self) -> Dict[str,str]:
        token = await self._token()
        url = f"https://api.netlify.com/api/v1/sites/{self.site_id}/env"
        headers = {"Authorization": f"Bearer {token}"}
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                r = await client.get(url, headers=headers)
                r.raise_for_status()
                data = r.json()  # [{"key":"X","values":[{"context":"all","value":"Y"}]}]
                out = {}
                for item in data:
                    key = item["key"]
                    vals = item.get("values") or []
                    if vals:
                        out[key] = vals[0].get("value","")
                return out
        except Exception:
            return {}

    async def upsert(self, kv: Dict[str,str]) -> List[str]:
        token = await self._token()
        url = f"https://api.netlify.com/api/v1/sites/{self.site_id}/env"
        headers = {"Authorization": f"Bearer {token}", "Content-Type":"application/json"}
        # Netlify expects array of {key, values: [{context, value}]}
        payload = [{"key":k,"values":[{"context":"all","value":v}]} for k,v in kv.items()]
        async with httpx.AsyncClient(timeout=20.0) as client:
            r = await client.patch(url, headers=headers, json=payload)
            r.raise_for_status()
        return list(kv.keys())
