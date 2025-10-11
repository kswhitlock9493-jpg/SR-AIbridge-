import os, pathlib, httpx
from typing import Optional, List
from ..config import CONFIG

async def from_env(name: str) -> Optional[str]:
    return os.getenv(name)

async def from_secret_files(name: str) -> Optional[str]:
    # check /etc/secrets/<filename> and ./secrets/<filename>
    candidates = []
    for fn in CONFIG.secret_filenames:
        # map heuristic: "RENDER_API_TOKEN" -> match filename containing "render"
        if fn.lower().startswith(name.split("_",1)[0].lower()):
            candidates += [f"/etc/secrets/{fn}", f"./secrets/{fn}"]
    for p in candidates:
        fp = pathlib.Path(p)
        if fp.exists():
            return fp.read_text().strip()
    return None

async def from_vault(name: str) -> Optional[str]:
    # expects Bridge Vault route: GET /bridge/vault/secret?key=NAME  (token-less in same process)
    # if your vault requires auth, wire here (we're in the backend).
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get("http://localhost:8000/bridge/vault/secret", params={"key": name})
            if r.status_code == 200:
                data = r.json()
                return data.get("value")
    except Exception:
        return None
    return None

async def from_dashboard_urls(name: str) -> Optional[str]:
    # optional: your admin dashboard can expose a one-shot bearer for envsync
    if not CONFIG.dashboard_token_urls:
        return None
    for url in CONFIG.dashboard_token_urls:
        try:
            async with httpx.AsyncClient(timeout=6.0) as client:
                r = await client.get(url, params={"key": name})
                if r.status_code == 200:
                    data = r.json()
                    token = data.get("value")
                    if token:
                        return token.strip()
        except Exception:
            continue
    return None
