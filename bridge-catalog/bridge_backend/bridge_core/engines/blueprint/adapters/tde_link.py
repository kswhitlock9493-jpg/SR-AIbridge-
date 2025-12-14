"""
TDE-X Link Adapter
Connects Blueprint Engine to TDE-X orchestrator for manifest preloading
"""
import logging
from typing import Dict, Any
from ..registry import BlueprintRegistry

logger = logging.getLogger(__name__)


async def preload_manifest() -> Dict[str, Any]:
    """
    Preload Blueprint manifest for TDE-X orchestrator validation.
    Called at TDE-X startup to validate shard definitions.
    
    Returns:
        Complete blueprint manifest
    """
    try:
        manifest = BlueprintRegistry.load_all()
        logger.info(f"[TDE-X Link] ✅ Preloaded {len(manifest)} engine blueprints")
        
        # Validate manifest integrity
        validation = BlueprintRegistry.validate_manifest_integrity()
        if not validation["valid"]:
            logger.warning(f"[TDE-X Link] ⚠️ Manifest validation warnings: {validation['errors']}")
        
        # Import event bus for publishing
        try:
            from ....heritage.event_bus import bus
            await bus.publish("blueprint.events", {
                "type": "manifest.loaded",
                "count": len(manifest),
                "timestamp": _get_timestamp()
            })
            logger.info("[TDE-X Link] 📡 Published manifest.loaded event")
        except Exception as e:
            logger.warning(f"[TDE-X Link] Could not publish event: {e}")
        
        return manifest
    except Exception as e:
        logger.error(f"[TDE-X Link] ❌ Failed to preload manifest: {e}")
        raise


def validate_shard(shard_name: str, manifest: Dict[str, Any]) -> bool:
    """
    Validate that a shard exists in the TDE-X blueprint.
    
    Args:
        shard_name: Name of the shard (bootstrap, runtime, diagnostics)
        manifest: Blueprint manifest from preload_manifest()
        
    Returns:
        True if shard is defined in blueprint, False otherwise
    """
    tde_x_blueprint = manifest.get("tde_x", {})
    shards = tde_x_blueprint.get("shards", [])
    
    valid = shard_name in shards
    if valid:
        logger.debug(f"[TDE-X Link] ✅ Shard '{shard_name}' validated")
    else:
        logger.warning(f"[TDE-X Link] ⚠️ Shard '{shard_name}' not found in blueprint")
    
    return valid


def _get_timestamp() -> str:
    """Get ISO timestamp"""
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat() + "Z"
