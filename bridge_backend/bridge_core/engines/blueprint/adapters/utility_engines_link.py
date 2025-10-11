"""
Utility Engines Link Adapter
Connects Blueprint Engine to utility engines: Creativity, Indoctrination, Screen, 
Speech, Recovery, Agents Foundry, Filing
"""
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

UTILITY_ENGINES = [
    "creativity",
    "indoctrination",
    "screen",
    "speech",
    "recovery",
    "agents_foundry",
    "filing"
]


def get_utility_engines_config(manifest: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract configuration for all utility engines from blueprint manifest.
    
    Args:
        manifest: Blueprint manifest
        
    Returns:
        Utility engines configuration mapping
    """
    config = {}
    
    for engine_name in UTILITY_ENGINES:
        engine_blueprint = manifest.get(engine_name, {})
        if engine_blueprint:
            config[engine_name] = {
                "name": engine_blueprint.get("name", ""),
                "description": engine_blueprint.get("description", ""),
                "schema": engine_blueprint.get("schema", {}),
                "topics": engine_blueprint.get("topics", []),
                "dependencies": engine_blueprint.get("dependencies", []),
                "available": True
            }
        else:
            config[engine_name] = {
                "available": False
            }
    
    return config


async def validate_utility_engines(manifest: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate that all utility engines are properly defined in the manifest.
    
    Args:
        manifest: Blueprint manifest
        
    Returns:
        Validation results for all utility engines
    """
    config = get_utility_engines_config(manifest)
    
    available = [name for name, cfg in config.items() if cfg.get("available", False)]
    missing = [name for name, cfg in config.items() if not cfg.get("available", False)]
    
    validation = {
        "all_available": len(missing) == 0,
        "available_count": len(available),
        "total_count": len(UTILITY_ENGINES),
        "available": available,
        "missing": missing
    }
    
    if validation["all_available"]:
        logger.info(f"[Utility Engines Link] ✅ All {len(UTILITY_ENGINES)} utility engines available")
    else:
        logger.warning(f"[Utility Engines Link] ⚠️ Missing utility engines: {missing}")
    
    return validation


async def initialize_utility_engines() -> Dict[str, Any]:
    """
    Initialize all utility engines with blueprint configuration.
    
    Returns:
        Initialization status
    """
    try:
        from ..registry import BlueprintRegistry
        
        manifest = BlueprintRegistry.load_all()
        config = get_utility_engines_config(manifest)
        
        initialized = []
        errors = []
        
        for engine_name, engine_config in config.items():
            if engine_config.get("available", False):
                try:
                    # Validate dependencies for engines that have them
                    dependencies = engine_config.get("dependencies", [])
                    missing_deps = [dep for dep in dependencies if dep not in manifest]
                    
                    if missing_deps:
                        errors.append(f"{engine_name}: missing dependencies {missing_deps}")
                    else:
                        initialized.append(engine_name)
                        
                except Exception as e:
                    errors.append(f"{engine_name}: {str(e)}")
        
        # Publish initialization event
        try:
            from ....heritage.event_bus import bus
            await bus.publish("blueprint.events", {
                "type": "utility_engines.initialized",
                "initialized": initialized,
                "errors": errors,
                "timestamp": _get_timestamp()
            })
            logger.info(f"[Utility Engines Link] 📡 Initialization event published")
        except Exception as e:
            logger.warning(f"[Utility Engines Link] ⚠️ Event bus publish failed: {e}")
        
        logger.info(f"[Utility Engines Link] ✅ {len(initialized)} utility engines initialized")
        
        return {
            "success": len(errors) == 0,
            "initialized": initialized,
            "errors": errors,
            "count": len(initialized),
            "timestamp": _get_timestamp()
        }
        
    except Exception as e:
        logger.error(f"[Utility Engines Link] ❌ Initialization failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "timestamp": _get_timestamp()
        }


def get_engine_manifest(engine_name: str, manifest: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get manifest for a specific utility engine.
    
    Args:
        engine_name: Name of the utility engine
        manifest: Blueprint manifest
        
    Returns:
        Engine manifest
    """
    if engine_name not in UTILITY_ENGINES:
        return {"error": "Not a utility engine"}
    
    engine_blueprint = manifest.get(engine_name, {})
    
    return {
        "engine": engine_name,
        "name": engine_blueprint.get("name", ""),
        "description": engine_blueprint.get("description", ""),
        "schema": engine_blueprint.get("schema", {}),
        "topics": engine_blueprint.get("topics", []),
        "dependencies": engine_blueprint.get("dependencies", []),
        "available": bool(engine_blueprint)
    }


def _get_timestamp() -> str:
    """Get ISO timestamp"""
    from datetime import datetime
    return datetime.utcnow().isoformat() + "Z"
