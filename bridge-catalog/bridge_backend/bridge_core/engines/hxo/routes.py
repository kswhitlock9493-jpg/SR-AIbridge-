"""
HXO Nexus Routes
FastAPI routes for HXO Nexus management and monitoring
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
import logging

from .nexus import get_nexus_instance, initialize_nexus
from .hypshard import HypShardV3Manager
from .security import SecurityLayerManager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/hxo", tags=["HXO Nexus"])


@router.get("/health")
async def get_nexus_health():
    """Get HXO Nexus health status"""
    try:
        nexus = get_nexus_instance()
        health = await nexus.health_check()
        return health
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/engines")
async def list_engines():
    """List all registered engines"""
    try:
        nexus = get_nexus_instance()
        engines = nexus.get_all_engines()
        return {
            "count": len(engines),
            "engines": engines
        }
    except Exception as e:
        logger.error(f"Failed to list engines: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/engines/{engine_id}")
async def get_engine_info(engine_id: str):
    """Get information about a specific engine"""
    try:
        nexus = get_nexus_instance()
        info = nexus.get_engine_info(engine_id)
        
        if info is None:
            raise HTTPException(status_code=404, detail="Engine not found")
        
        return info
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get engine info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/connections")
async def get_connection_graph():
    """Get the complete engine connection topology"""
    try:
        nexus = get_nexus_instance()
        graph = nexus.get_connection_graph()
        
        # Calculate statistics
        total_connections = sum(len(conns) for conns in graph.values())
        
        return {
            "graph": graph,
            "statistics": {
                "total_engines": len(graph),
                "total_connections": total_connections,
                "avg_connections": total_connections / len(graph) if graph else 0
            }
        }
    except Exception as e:
        logger.error(f"Failed to get connection graph: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/connections/{engine_a}/{engine_b}")
async def check_connection(engine_a: str, engine_b: str):
    """Check if two engines are connected"""
    try:
        nexus = get_nexus_instance()
        is_connected = nexus.is_connected(engine_a, engine_b)
        
        return {
            "engine_a": engine_a,
            "engine_b": engine_b,
            "connected": is_connected
        }
    except Exception as e:
        logger.error(f"Failed to check connection: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/coordinate")
async def coordinate_engines(intent: Dict[str, Any]):
    """Coordinate multiple engines to fulfill an intent"""
    try:
        nexus = get_nexus_instance()
        result = await nexus.coordinate_engines(intent)
        return result
    except Exception as e:
        logger.error(f"Coordination failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/initialize")
async def initialize_hxo_nexus():
    """Initialize the HXO Nexus"""
    try:
        nexus = await initialize_nexus()
        health = await nexus.health_check()
        return {
            "status": "initialized",
            "health": health
        }
    except Exception as e:
        logger.error(f"Initialization failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/config")
async def get_nexus_config():
    """Get HXO Nexus configuration"""
    try:
        import json
        from pathlib import Path
        
        config_path = Path(__file__).parent / "nexus_config.json"
        
        if not config_path.exists():
            raise HTTPException(status_code=404, detail="Configuration not found")
        
        with open(config_path, "r") as f:
            config = json.load(f)
        
        return config
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get config: {e}")
        raise HTTPException(status_code=500, detail=str(e))
