from typing import Optional
from . import sources
from ..config import CONFIG

DISPATCH = {
    "env": sources.from_env,
    "secret_files": sources.from_secret_files,
    "vault": sources.from_vault,
    "dashboard": sources.from_dashboard_urls,
}

async def discover_token(name: str) -> Optional[str]:
    for step in CONFIG.discovery_order:
        fn = DISPATCH.get(step)
        if not fn: 
            continue
        try:
            val = await fn(name)
            if val:
                return val
        except Exception:
            continue
    return None
