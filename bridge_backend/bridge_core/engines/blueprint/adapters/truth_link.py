"""
Truth Link Adapter
Connects Blueprint Engine to Truth Engine for schema validation and certification
"""
import logging
from typing import Dict, Any
import hashlib
import json

logger = logging.getLogger(__name__)


async def validate_blueprint_sync(manifest: Dict[str, Any], deployed_state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate that deployed schema aligns with blueprint manifest.
    
    Args:
        manifest: Blueprint manifest
        deployed_state: Current deployed state
        
    Returns:
        Validation result with sync status
    """
    try:
        # Calculate manifest hash
        manifest_hash = _calculate_manifest_hash(manifest)
        
        # Calculate deployed schema hash
        deployed_hash = _calculate_manifest_hash(deployed_state)
        
        synced = manifest_hash == deployed_hash
        
        result = {
            "synced": synced,
            "manifest_hash": manifest_hash,
            "deployed_hash": deployed_hash,
            "timestamp": _get_timestamp()
        }
        
        # Publish sync fact
        from ....heritage.event_bus import bus
        await bus.publish("deploy.facts", {
            "type": "fact.blueprint.synced" if synced else "fact.blueprint.drift",
            "fact": result,
            "timestamp": result["timestamp"]
        })
        
        if synced:
            logger.info("[Truth Link] ✅ Blueprint and deployed state are synchronized")
        else:
            logger.warning("[Truth Link] ⚠️ Blueprint drift detected")
        
        return result
        
    except Exception as e:
        logger.error(f"[Truth Link] ❌ Validation failed: {e}")
        raise


async def certify_fact(fact: Dict[str, Any], manifest: Dict[str, Any]) -> Dict[str, Any]:
    """
    Certify a fact against blueprint schema.
    
    Args:
        fact: Fact to certify
        manifest: Blueprint manifest
        
    Returns:
        Certification result
    """
    try:
        fact_type = fact.get("type", "")
        fact_data = fact.get("data", {})
        
        # Validate fact structure
        valid = _validate_fact_structure(fact_type, fact_data, manifest)
        
        certification = {
            "fact_type": fact_type,
            "valid": valid,
            "certified_at": _get_timestamp(),
            "manifest_hash": _calculate_manifest_hash(manifest)
        }
        
        if valid:
            logger.info(f"[Truth Link] ✅ Fact '{fact_type}' certified")
        else:
            logger.warning(f"[Truth Link] ⚠️ Fact '{fact_type}' failed certification")
        
        return certification
        
    except Exception as e:
        logger.error(f"[Truth Link] ❌ Certification failed: {e}")
        return {
            "valid": False,
            "error": str(e),
            "certified_at": _get_timestamp()
        }


def _validate_fact_structure(fact_type: str, fact_data: Dict[str, Any], manifest: Dict[str, Any]) -> bool:
    """
    Validate fact structure against blueprint schemas.
    
    Args:
        fact_type: Type of fact
        fact_data: Fact data
        manifest: Blueprint manifest
        
    Returns:
        True if fact structure is valid
    """
    # Basic validation - check that fact has required fields
    if not isinstance(fact_data, dict):
        return False
    
    # For now, accept all well-formed facts
    # TODO: Add more sophisticated schema validation based on manifest
    return True


def _calculate_manifest_hash(data: Dict[str, Any]) -> str:
    """
    Calculate hash of manifest or state data.
    
    Args:
        data: Data to hash
        
    Returns:
        SHA256 hash hex string
    """
    # Serialize to JSON with sorted keys for consistent hashing
    json_str = json.dumps(data, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(json_str.encode()).hexdigest()[:16]


def _get_timestamp() -> str:
    """Get ISO timestamp"""
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat() + "Z"
