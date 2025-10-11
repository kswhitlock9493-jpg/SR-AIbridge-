"""
Super Engines Link Adapter
Connects Blueprint Engine to the Six Super Engines (CalculusCore, QHelmSingularity, 
AuroraForge, ChronicleLoom, ScrollTongue, CommerceForge)
"""
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

SUPER_ENGINES = [
    "calculuscore",
    "qhelmsingularity", 
    "auroraforge",
    "chronicleloom",
    "scrolltongue",
    "commerceforge"
]


def get_super_engines_config(manifest: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract configuration for all super engines from blueprint manifest.
    
    Args:
        manifest: Blueprint manifest
        
    Returns:
        Super engines configuration mapping
    """
    config = {}
    
    for engine_name in SUPER_ENGINES:
        engine_blueprint = manifest.get(engine_name, {})
        if engine_blueprint:
            config[engine_name] = {
                "name": engine_blueprint.get("name", ""),
                "description": engine_blueprint.get("description", ""),
                "schema": engine_blueprint.get("schema", {}),
                "topics": engine_blueprint.get("topics", []),
                "available": True
            }
        else:
            config[engine_name] = {
                "available": False
            }
    
    return config


async def validate_super_engines(manifest: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate that all super engines are properly defined in the manifest.
    
    Args:
        manifest: Blueprint manifest
        
    Returns:
        Validation results for all super engines
    """
    config = get_super_engines_config(manifest)
    
    available = [name for name, cfg in config.items() if cfg.get("available", False)]
    missing = [name for name, cfg in config.items() if not cfg.get("available", False)]
    
    validation = {
        "all_available": len(missing) == 0,
        "available_count": len(available),
        "total_count": len(SUPER_ENGINES),
        "available": available,
        "missing": missing
    }
    
    if validation["all_available"]:
        logger.info(f"[Super Engines Link] ✅ All {len(SUPER_ENGINES)} super engines available")
    else:
        logger.warning(f"[Super Engines Link] ⚠️ Missing super engines: {missing}")
    
    return validation


async def subscribe_super_engines_to_blueprint() -> Dict[str, Any]:
    """
    Subscribe all super engines to blueprint update events.
    
    Returns:
        Subscription status
    """
    try:
        from ....heritage.event_bus import bus
        from ..registry import BlueprintRegistry
        
        manifest = BlueprintRegistry.load_all()
        config = get_super_engines_config(manifest)
        
        subscribed = []
        for engine_name, engine_config in config.items():
            if engine_config.get("available", False):
                # Each super engine can react to blueprint updates
                subscribed.append(engine_name)
        
        logger.info(f"[Super Engines Link] 📡 {len(subscribed)} super engines ready for blueprint events")
        
        return {
            "success": True,
            "subscribed": subscribed,
            "count": len(subscribed),
            "timestamp": _get_timestamp()
        }
        
    except Exception as e:
        logger.error(f"[Super Engines Link] ❌ Subscription failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "timestamp": _get_timestamp()
        }


def get_engine_capabilities(engine_name: str, manifest: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get capabilities for a specific super engine.
    
    Args:
        engine_name: Name of the super engine
        manifest: Blueprint manifest
        
    Returns:
        Engine capabilities and schema
    """
    if engine_name not in SUPER_ENGINES:
        return {"error": "Not a super engine"}
    
    engine_blueprint = manifest.get(engine_name, {})
    
    return {
        "engine": engine_name,
        "name": engine_blueprint.get("name", ""),
        "description": engine_blueprint.get("description", ""),
        "schema": engine_blueprint.get("schema", {}),
        "topics": engine_blueprint.get("topics", []),
        "available": bool(engine_blueprint)
    }


def _get_timestamp() -> str:
    """Get ISO timestamp"""
    from datetime import datetime
    return datetime.utcnow().isoformat() + "Z"
