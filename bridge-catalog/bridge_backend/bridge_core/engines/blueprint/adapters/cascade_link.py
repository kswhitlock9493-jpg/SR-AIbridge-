"""
Cascade Link Adapter
Connects Blueprint Engine to Cascade Engine for automatic DAG regeneration
"""
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


async def subscribe_to_blueprint_updates():
    """
    Subscribe Cascade engine to Blueprint change events.
    Automatically rebuilds DAG when Blueprint definitions evolve.
    """
    try:
        from ....heritage.event_bus import bus
        
        # Subscribe to blueprint.events topic
        bus.subscribe("blueprint.events", handle_blueprint_event)
        logger.info("[Cascade Link] 📡 Subscribed to blueprint.events")
    except Exception as e:
        logger.error(f"[Cascade Link] ❌ Failed to subscribe: {e}")


async def handle_blueprint_event(event: Dict[str, Any]):
    """
    Handle blueprint events and trigger DAG rebuild when needed.
    
    Args:
        event: Event payload from blueprint.events topic
    """
    event_type = event.get("type", "")
    
    if event_type == "manifest.loaded":
        logger.info("[Cascade Link] 📋 Blueprint manifest loaded")
        # DAG will be built on-demand, no immediate action needed
    
    elif event_type == "update":
        logger.info("[Cascade Link] 🔄 Blueprint updated, triggering DAG rebuild")
        await rebuild_dag(event)
    
    else:
        logger.debug(f"[Cascade Link] Received event type: {event_type}")


async def rebuild_dag(event: Dict[str, Any]):
    """
    Rebuild Cascade DAG based on updated blueprint.
    
    Args:
        event: Blueprint update event
    """
    try:
        from ..registry import BlueprintRegistry
        
        # Load latest blueprint manifest
        manifest = BlueprintRegistry.load_all()
        
        # Extract cascade-specific configuration
        cascade_blueprint = manifest.get("cascade", {})
        dependencies = cascade_blueprint.get("dependencies", [])
        
        logger.info(f"[Cascade Link] 📊 Rebuilding DAG with {len(dependencies)} dependencies")
        
        # Publish rebuild event
        from ....heritage.event_bus import bus
        await bus.publish("deploy.graph", {
            "type": "dag.rebuild",
            "dependencies": dependencies,
            "timestamp": _get_timestamp()
        })
        
        logger.info("[Cascade Link] ✅ DAG rebuild triggered")
        
    except Exception as e:
        logger.error(f"[Cascade Link] ❌ DAG rebuild failed: {e}")


def get_cascade_config(manifest: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract Cascade configuration from blueprint manifest.
    
    Args:
        manifest: Blueprint manifest
        
    Returns:
        Cascade-specific configuration
    """
    cascade_blueprint = manifest.get("cascade", {})
    return {
        "name": cascade_blueprint.get("name", "Cascade Engine"),
        "description": cascade_blueprint.get("description", ""),
        "schema": cascade_blueprint.get("schema", {}),
        "topics": cascade_blueprint.get("topics", []),
        "dependencies": cascade_blueprint.get("dependencies", [])
    }


def _get_timestamp() -> str:
    """Get ISO timestamp"""
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat() + "Z"
