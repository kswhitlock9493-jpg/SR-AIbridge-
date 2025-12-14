"""
Umbra Cascade Link Adapter
Connects Umbra Lattice to Cascade for propagation tracking
"""

import logging
from typing import Dict, Any
from datetime import datetime, UTC

logger = logging.getLogger(__name__)


async def track_cascade_propagation(cascade_event: Dict[str, Any]):
    """
    Track Cascade propagation in Umbra Lattice
    
    Args:
        cascade_event: Cascade event data
    """
    try:
        from bridge_backend.bridge_core.engines.umbra.lattice import UmbraLattice
        
        lattice = UmbraLattice()
        await lattice.initialize()
        
        # Convert cascade event to lattice event
        lattice_event = {
            "type": "cascade_propagation",
            "action": cascade_event.get("action"),
            "source": cascade_event.get("source"),
            "target": cascade_event.get("target"),
            "status": cascade_event.get("status"),
            "ts": cascade_event.get("timestamp", datetime.now(UTC).isoformat())
        }
        
        # Record to lattice
        await lattice.record_event(lattice_event)
        
        logger.debug(f"[Umbra Cascade Link] Tracked cascade: {cascade_event.get('action')}")
        
    except ImportError:
        logger.debug("[Umbra Cascade Link] Umbra Lattice not available")
    except Exception as e:
        logger.error(f"[Umbra Cascade Link] Failed to track cascade: {e}")


async def subscribe_to_cascade():
    """
    Subscribe to Cascade events for tracking
    """
    try:
        from bridge_backend.genesis.bus import genesis_bus
        
        if not genesis_bus.is_enabled():
            logger.debug("[Umbra Cascade Link] Genesis bus disabled")
            return
        
        # Subscribe to cascade-related topics
        cascade_topics = [
            "genesis.heal",
            "cascade.propagate",
            "cascade.complete"
        ]
        
        for topic in cascade_topics:
            genesis_bus.subscribe(topic, track_cascade_propagation)
            logger.debug(f"[Umbra Cascade Link] Subscribed to {topic}")
        
        logger.info(f"✅ Umbra Cascade Link subscribed to {len(cascade_topics)} topics")
        
    except ImportError:
        logger.debug("[Umbra Cascade Link] Genesis bus not available")
    except Exception as e:
        logger.error(f"[Umbra Cascade Link] Failed to subscribe: {e}")
