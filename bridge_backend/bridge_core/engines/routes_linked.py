"""
Linked Engines Routes
Initializes Blueprint Engine linkages with all engines under Genesis unification
v1.9.7c - Genesis Linkage (Unified)
Includes: TDE-X, Cascade, Truth, Autonomy, Parser, Leviathan, Super Engines, and Utility Engines
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging
import os

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/engines/linked", tags=["engines-linked"])

# Check if linkage is enabled
LINK_ENGINES = os.getenv("LINK_ENGINES", "false").lower() == "true"


@router.get("/status")
async def linkage_status() -> Dict[str, Any]:
    """
    Get status of engine linkages.
    
    Returns:
        Status of all engine linkages
    """
    if not LINK_ENGINES:
        return {
            "enabled": False,
            "message": "Engine linkage not enabled. Set LINK_ENGINES=true to enable."
        }
    
    try:
        from .blueprint.registry import BlueprintRegistry
        
        # Load manifest
        manifest = BlueprintRegistry.load_all()
        
        # Validate integrity
        validation = BlueprintRegistry.validate_manifest_integrity()
        
        return {
            "enabled": True,
            "engines": list(manifest.keys()),
            "count": len(manifest),
            "validation": validation,
            "linkages": {
                "tde_x": "Blueprint → TDE-X manifest preloading",
                "cascade": "Blueprint → Cascade DAG auto-rebuild",
                "truth": "Blueprint → Truth schema validation",
                "autonomy": "Blueprint → Autonomy guardrails",
                "parser": "Blueprint → Parser content ingestion",
                "leviathan": "Blueprint → Leviathan unified solver",
                "super_engines": "Blueprint → Six Super Engines (CalculusCore, QHelmSingularity, AuroraForge, ChronicleLoom, ScrollTongue, CommerceForge)",
                "utility_engines": "Blueprint → Utility Engines (Creativity, Indoctrination, Screen, Speech, Recovery, AgentsFoundry, Filing)"
            }
        }
    except Exception as e:
        logger.error(f"Error getting linkage status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/manifest")
async def get_manifest() -> Dict[str, Any]:
    """
    Get complete Blueprint manifest.
    
    Returns:
        Full blueprint manifest with all engine definitions
    """
    if not LINK_ENGINES:
        raise HTTPException(
            status_code=503,
            detail="Engine linkage not enabled. Set LINK_ENGINES=true to enable."
        )
    
    try:
        from .blueprint.registry import BlueprintRegistry
        manifest = BlueprintRegistry.load_all()
        return manifest
    except Exception as e:
        logger.error(f"Error loading manifest: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/manifest/{engine_name}")
async def get_engine_manifest(engine_name: str) -> Dict[str, Any]:
    """
    Get Blueprint manifest for a specific engine.
    
    Args:
        engine_name: Name of the engine
        
    Returns:
        Blueprint for the specified engine
    """
    if not LINK_ENGINES:
        raise HTTPException(
            status_code=503,
            detail="Engine linkage not enabled. Set LINK_ENGINES=true to enable."
        )
    
    try:
        from .blueprint.registry import BlueprintRegistry
        engine = BlueprintRegistry.get_engine(engine_name)
        
        if not engine:
            raise HTTPException(
                status_code=404,
                detail=f"Engine '{engine_name}' not found in manifest"
            )
        
        return engine
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error loading engine manifest: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/initialize")
async def initialize_linkages() -> Dict[str, Any]:
    """
    Initialize all engine linkages.
    Sets up event subscriptions and validates connections.
    
    Returns:
        Initialization results
    """
    if not LINK_ENGINES:
        raise HTTPException(
            status_code=503,
            detail="Engine linkage not enabled. Set LINK_ENGINES=true to enable."
        )
    
    try:
        results = {
            "initialized": [],
            "errors": []
        }
        
        # Initialize Cascade subscription to Blueprint events
        try:
            from .blueprint.adapters import cascade_link
            await cascade_link.subscribe_to_blueprint_updates()
            results["initialized"].append("cascade")
            logger.info("✅ Cascade linkage initialized")
        except Exception as e:
            results["errors"].append(f"cascade: {str(e)}")
            logger.error(f"❌ Cascade linkage failed: {e}")
        
        # Initialize Super Engines linkage
        try:
            from .blueprint.adapters import super_engines_link
            await super_engines_link.subscribe_super_engines_to_blueprint()
            results["initialized"].append("super_engines")
            logger.info("✅ Super Engines linkage initialized")
        except Exception as e:
            results["errors"].append(f"super_engines: {str(e)}")
            logger.error(f"❌ Super Engines linkage failed: {e}")
        
        # Initialize Utility Engines linkage
        try:
            from .blueprint.adapters import utility_engines_link
            await utility_engines_link.initialize_utility_engines()
            results["initialized"].append("utility_engines")
            logger.info("✅ Utility Engines linkage initialized")
        except Exception as e:
            results["errors"].append(f"utility_engines: {str(e)}")
            logger.error(f"❌ Utility Engines linkage failed: {e}")
        
        # Validate Blueprint manifest
        try:
            from .blueprint.registry import BlueprintRegistry
            validation = BlueprintRegistry.validate_manifest_integrity()
            results["validation"] = validation
            logger.info("✅ Blueprint manifest validated")
        except Exception as e:
            results["errors"].append(f"validation: {str(e)}")
            logger.error(f"❌ Manifest validation failed: {e}")
        
        return results
        
    except Exception as e:
        logger.error(f"Error initializing linkages: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dependencies/{engine_name}")
async def get_engine_dependencies(engine_name: str) -> Dict[str, Any]:
    """
    Get dependencies for a specific engine.
    
    Args:
        engine_name: Name of the engine
        
    Returns:
        List of engine dependencies
    """
    if not LINK_ENGINES:
        raise HTTPException(
            status_code=503,
            detail="Engine linkage not enabled. Set LINK_ENGINES=true to enable."
        )
    
    try:
        from .blueprint.registry import BlueprintRegistry
        dependencies = BlueprintRegistry.get_dependencies(engine_name)
        topics = BlueprintRegistry.get_topics(engine_name)
        
        return {
            "engine": engine_name,
            "dependencies": dependencies,
            "topics": topics
        }
    except Exception as e:
        logger.error(f"Error getting dependencies: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/super-engines/status")
async def get_super_engines_status() -> Dict[str, Any]:
    """
    Get status of all super engines.
    
    Returns:
        Validation and status of all six super engines
    """
    if not LINK_ENGINES:
        raise HTTPException(
            status_code=503,
            detail="Engine linkage not enabled. Set LINK_ENGINES=true to enable."
        )
    
    try:
        from .blueprint.registry import BlueprintRegistry
        from .blueprint.adapters import super_engines_link
        
        manifest = BlueprintRegistry.load_all()
        validation = await super_engines_link.validate_super_engines(manifest)
        config = super_engines_link.get_super_engines_config(manifest)
        
        return {
            "validation": validation,
            "engines": config,
            "super_engines": super_engines_link.SUPER_ENGINES
        }
    except Exception as e:
        logger.error(f"Error getting super engines status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/utility-engines/status")
async def get_utility_engines_status() -> Dict[str, Any]:
    """
    Get status of all utility engines.
    
    Returns:
        Validation and status of all utility engines
    """
    if not LINK_ENGINES:
        raise HTTPException(
            status_code=503,
            detail="Engine linkage not enabled. Set LINK_ENGINES=true to enable."
        )
    
    try:
        from .blueprint.registry import BlueprintRegistry
        from .blueprint.adapters import utility_engines_link
        
        manifest = BlueprintRegistry.load_all()
        validation = await utility_engines_link.validate_utility_engines(manifest)
        config = utility_engines_link.get_utility_engines_config(manifest)
        
        return {
            "validation": validation,
            "engines": config,
            "utility_engines": utility_engines_link.UTILITY_ENGINES
        }
    except Exception as e:
        logger.error(f"Error getting utility engines status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/leviathan/status")
async def get_leviathan_status() -> Dict[str, Any]:
    """
    Get status of Leviathan solver and its super engine coordination.
    
    Returns:
        Leviathan configuration and super engine validation
    """
    if not LINK_ENGINES:
        raise HTTPException(
            status_code=503,
            detail="Engine linkage not enabled. Set LINK_ENGINES=true to enable."
        )
    
    try:
        from .blueprint.registry import BlueprintRegistry
        from .blueprint.adapters import leviathan_link
        
        manifest = BlueprintRegistry.load_all()
        leviathan_config = leviathan_link.get_leviathan_config(manifest)
        validation = await leviathan_link.validate_solver_blueprint(manifest)
        
        return {
            "config": leviathan_config,
            "validation": validation,
            "super_engines_coordination": validation["available"]
        }
    except Exception as e:
        logger.error(f"Error getting Leviathan status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

