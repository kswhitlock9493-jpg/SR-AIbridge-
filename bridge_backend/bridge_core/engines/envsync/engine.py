import os
from typing import Dict, List
from .config import CONFIG
from .types import SyncResult, Mode
from .providers.render import RenderProvider
from .providers.netlify import NetlifyProvider
from .providers.base import ProviderBase
from .diffs import compute_diff
from .telemetry import ticket

def _is_included(key: str) -> bool:
    if any(key.startswith(p) for p in CONFIG.exclude_prefixes):
        return False
    if CONFIG.include_prefixes:
        return any(key.startswith(p) for p in CONFIG.include_prefixes)
    return True

def _canonical_from_env() -> Dict[str,str]:
    out = {}
    for k,v in os.environ.items():
        if _is_included(k):
            out[k] = v
    return out

# NOTE: for 'vault' or 'file' canonical sources, you can expand here.
def load_canonical() -> Dict[str,str]:
    # For now, env is the easiest canonical snapshot + your Vault route can be added later.
    return _canonical_from_env()

def provider_for(name: str) -> ProviderBase:
    if name == "render":
        return RenderProvider(service_id=os.getenv("RENDER_SERVICE_ID",""))
    if name == "netlify":
        return NetlifyProvider(site_id=os.getenv("NETLIFY_SITE_ID",""))
    raise ValueError(f"Unknown provider {name}")

async def sync_provider(name: str, mode: Mode="enforce") -> SyncResult:
    prov = provider_for(name)
    canonical = load_canonical()
    remote = await prov.fetch()

    diff = compute_diff(canonical, remote, CONFIG.allow_deletions)
    apply_create = {d["key"]: d["to_val"] for d in diff if d["op"] in ("create","update")}
    deletes = [d["key"] for d in diff if d["op"] == "delete"]

    applied = False
    errors: List[str] = []

    if mode == "enforce" and (apply_create or deletes):
        try:
            if apply_create:
                await prov.upsert(apply_create)
            if deletes:
                await prov.delete(deletes)  # no-op in provider if unsupported
            applied = True
        except Exception as e:
            errors.append(str(e))
            ticket(f"EnvSync failure: {name}", f"Error applying: {e}")

    return {
        "provider": name,
        "mode": mode,
        "applied": applied,
        "diff": diff,
        "errors": errors,
    }
