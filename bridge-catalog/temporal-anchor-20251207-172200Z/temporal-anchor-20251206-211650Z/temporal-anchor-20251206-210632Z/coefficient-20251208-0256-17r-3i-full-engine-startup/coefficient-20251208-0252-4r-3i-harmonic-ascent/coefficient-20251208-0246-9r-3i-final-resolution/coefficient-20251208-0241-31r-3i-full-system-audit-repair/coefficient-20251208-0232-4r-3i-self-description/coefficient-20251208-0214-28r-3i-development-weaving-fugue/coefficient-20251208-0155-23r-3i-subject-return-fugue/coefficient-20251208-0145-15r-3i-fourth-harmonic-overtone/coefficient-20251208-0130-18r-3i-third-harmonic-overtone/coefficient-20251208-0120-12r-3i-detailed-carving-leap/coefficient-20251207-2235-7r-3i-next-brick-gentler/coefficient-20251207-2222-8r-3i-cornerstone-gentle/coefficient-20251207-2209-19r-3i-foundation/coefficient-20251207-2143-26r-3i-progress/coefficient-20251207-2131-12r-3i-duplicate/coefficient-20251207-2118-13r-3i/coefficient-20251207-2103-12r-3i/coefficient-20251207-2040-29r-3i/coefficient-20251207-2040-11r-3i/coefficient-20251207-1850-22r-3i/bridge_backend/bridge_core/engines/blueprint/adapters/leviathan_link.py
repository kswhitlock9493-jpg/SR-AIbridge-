"""
Leviathan Link Adapter
Connects Blueprint Engine to Leviathan Solver for unified problem solving
"""
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


def get_leviathan_config(manifest: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract Leviathan configuration from blueprint manifest.
    
    Args:
        manifest: Blueprint manifest
        
    Returns:
        Leviathan-specific configuration
    """
    leviathan_blueprint = manifest.get("leviathan", {})
    return {
        "name": leviathan_blueprint.get("name", "Leviathan Solver"),
        "description": leviathan_blueprint.get("description", ""),
        "schema": leviathan_blueprint.get("schema", {}),
        "topics": leviathan_blueprint.get("topics", []),
        "dependencies": leviathan_blueprint.get("dependencies", []),
        "super_engines": [
            "calculuscore",
            "qhelmsingularity", 
            "auroraforge",
            "chronicleloom",
            "scrolltongue",
            "commerceforge"
        ]
    }


async def coordinate_super_engines(query: Dict[str, Any]) -> Dict[str, Any]:
    """
    Coordinate all super engines for complex problem solving.
    
    Args:
        query: Query to process across super engines
        
    Returns:
        Coordinated results from all super engines
    """
    try:
        from ..registry import BlueprintRegistry
        
        # Load manifest to get super engine configurations
        manifest = BlueprintRegistry.load_all()
        leviathan_config = get_leviathan_config(manifest)
        
        results = {
            "query": query,
            "super_engines": leviathan_config["super_engines"],
            "coordinated": True,
            "timestamp": _get_timestamp()
        }
        
        # Publish coordination event
        try:
            from ....heritage.event_bus import bus
            await bus.publish("solver.tasks", {
                "type": "super_engines.coordinated",
                "query": query,
                "engines": leviathan_config["super_engines"],
                "timestamp": _get_timestamp()
            })
            logger.info("[Leviathan Link] 🔗 Super engines coordination event published")
        except Exception as e:
            logger.warning(f"[Leviathan Link] ⚠️ Event bus publish failed: {e}")
        
        return results
        
    except Exception as e:
        logger.error(f"[Leviathan Link] ❌ Super engine coordination failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "timestamp": _get_timestamp()
        }


async def validate_solver_blueprint(manifest: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate that Leviathan solver has access to all required super engines.
    
    Args:
        manifest: Blueprint manifest
        
    Returns:
        Validation results
    """
    leviathan_config = get_leviathan_config(manifest)
    super_engines = leviathan_config["super_engines"]
    
    missing = []
    available = []
    
    for engine in super_engines:
        if engine in manifest:
            available.append(engine)
        else:
            missing.append(engine)
    
    return {
        "valid": len(missing) == 0,
        "available": available,
        "missing": missing,
        "total_required": len(super_engines),
        "total_available": len(available)
    }


def _get_timestamp() -> str:
    """Get ISO timestamp"""
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat() + "Z"
