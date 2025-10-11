"""
Linked Engines Routes
Initializes Blueprint Engine linkages with TDE-X, Cascade, Truth, and Autonomy engines
v1.9.7c - Genesis Linkage
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
        from ..blueprint.registry import BlueprintRegistry
        
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
                "autonomy": "Blueprint → Autonomy guardrails"
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
        from ..blueprint.registry import BlueprintRegistry
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
        from ..blueprint.registry import BlueprintRegistry
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
            from ..blueprint.adapters import cascade_link
            await cascade_link.subscribe_to_blueprint_updates()
            results["initialized"].append("cascade")
            logger.info("✅ Cascade linkage initialized")
        except Exception as e:
            results["errors"].append(f"cascade: {str(e)}")
            logger.error(f"❌ Cascade linkage failed: {e}")
        
        # Validate Blueprint manifest
        try:
            from ..blueprint.registry import BlueprintRegistry
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
        from ..blueprint.registry import BlueprintRegistry
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
