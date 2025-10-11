import os
import logging
from pathlib import Path
from typing import Dict, List
from .config import CONFIG
from .types import SyncResult, Mode
from .providers.render import RenderProvider
from .providers.netlify import NetlifyProvider
from .providers.base import ProviderBase
from .diffs import compute_diff
from .telemetry import ticket

logger = logging.getLogger(__name__)

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

def _canonical_from_seed_manifest() -> Dict[str, str]:
    """
    Load canonical environment variables from the EnvSync Seed Manifest.
    This manifest serves as the single source of truth for Genesis v2.0.1a.
    """
    manifest_path = Path(__file__).parent.parent.parent.parent / ".genesis" / "envsync_seed_manifest.env"
    
    if not manifest_path.exists():
        logger.warning(f"⚠️ EnvSync Seed Manifest not found at {manifest_path}")
        return {}
    
    canonical = {}
    try:
        with open(manifest_path, 'r') as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue
                # Parse KEY=VALUE format
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    # Only include if it passes the filter
                    if _is_included(key):
                        canonical[key] = value
        
        logger.info(f"✅ Loaded {len(canonical)} variables from EnvSync Seed Manifest")
    except Exception as e:
        logger.error(f"❌ Failed to load EnvSync Seed Manifest: {e}")
        return {}
    
    return canonical

# NOTE: for 'vault' or 'file' canonical sources, you can expand here.
def load_canonical() -> Dict[str,str]:
    """
    Load canonical environment variables based on configured source.
    
    Sources (in order of precedence):
    1. 'file' - Load from EnvSync Seed Manifest
    2. 'vault' - Load from Bridge Vault (future enhancement)
    3. 'env' - Load from current environment variables
    """
    source = CONFIG.canonical_source
    
    if source == "file":
        # Load from seed manifest file
        canonical = _canonical_from_seed_manifest()
        if canonical:
            return canonical
        logger.warning("⚠️ Falling back to environment variables")
    
    # Default to environment variables
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
    
    # Notify Autonomy & Genesis of drift or completion
    try:
        from bridge_backend.bridge_core.engines.adapters.envsync_autonomy_link import envsync_autonomy_link
        
        changed = [d for d in diff if d["op"] in ("create","update","delete")]
        if changed or errors:
            await envsync_autonomy_link.notify_drift_detected(name, len(changed), errors)
        
        if mode == "enforce":
            await envsync_autonomy_link.notify_sync_complete(name, applied, len(changed))
    except Exception:
        # Link is optional; don't fail if Autonomy/Genesis not available
        pass

    return {
        "provider": name,
        "mode": mode,
        "applied": applied,
        "diff": diff,
        "errors": errors,
    }
