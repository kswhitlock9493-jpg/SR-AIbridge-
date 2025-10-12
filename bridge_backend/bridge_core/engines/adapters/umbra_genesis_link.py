"""
Umbra Genesis Link Adapter
Subscribes Umbra Lattice to Genesis event topics
"""

import logging
from typing import Dict, Any
from datetime import datetime, UTC

logger = logging.getLogger(__name__)


async def subscribe_umbra_to_genesis():
    """
    Subscribe Umbra Lattice to relevant Genesis topics
    
    Topics monitored:
    - deploy.* (deploy events)
    - envrecon.* (environment reconciliation)
    - arie.* (autonomous repository integrity)
    - chimera.* (deployment engine)
    - netlify.* (Netlify events)
    - render.* (Render events)
    - github.* (GitHub events)
    - truth.* (truth certification)
    - cascade.* (cascade propagation)
    """
    try:
        from bridge_backend.genesis.bus import genesis_bus
        from bridge_backend.bridge_core.engines.umbra.lattice import UmbraLattice
        
        if not genesis_bus.is_enabled():
            logger.debug("[Umbra Genesis Link] Genesis bus disabled")
            return
        
        lattice = UmbraLattice()
        await lattice.initialize()
        
        # Define event handler
        async def handle_event(event: Dict[str, Any]):
            """Handle incoming Genesis event"""
            try:
                await lattice.record_event(event)
                logger.debug(f"[Umbra Genesis Link] Recorded event: {event.get('type')}")
            except Exception as e:
                logger.error(f"[Umbra Genesis Link] Failed to record event: {e}")
        
        # Subscribe to topics
        topics = [
            # Deploy topics
            "deploy.initiated",
            "deploy.heal.intent",
            "deploy.heal.complete",
            "deploy.certified",
            "deploy.netlify",
            "deploy.render",
            "deploy.github",
            "deploy.platform.start",
            "deploy.platform.success",
            "deploy.platform.failure",
            
            # EnvRecon topics
            "envrecon.drift",
            "envrecon.audit",
            "envrecon.heal",
            "envrecon.sync",
            
            # ARIE topics
            "arie.audit",
            "arie.fix.intent",
            "arie.fix.applied",
            "arie.fix.rollback",
            "arie.alert",
            
            # Chimera topics
            "chimera.simulate.start",
            "chimera.simulate.complete",
            "chimera.deploy.start",
            "chimera.deploy.complete",
            "chimera.certify.start",
            "chimera.certify.complete",
            "chimera.rollback.triggered",
            
            # Netlify topics (from engines)
            "deploy.netlify.preview_failed",
            
            # Truth topics
            "genesis.fact",
            
            # Cascade topics
            "genesis.heal",
            
            # Autonomy topics
            "autonomy.heal.applied",
            "autonomy.heal.error",
        ]
        
        for topic in topics:
            genesis_bus.subscribe(topic, handle_event)
            logger.debug(f"[Umbra Genesis Link] Subscribed to {topic}")
        
        logger.info(f"✅ Umbra Lattice subscribed to {len(topics)} Genesis topics")
        
    except ImportError:
        logger.debug("[Umbra Genesis Link] Genesis bus not available")
    except Exception as e:
        logger.error(f"[Umbra Genesis Link] Failed to subscribe: {e}")


async def publish_lattice_event(event_type: str, data: Dict[str, Any]):
    """
    Publish Umbra Lattice event to Genesis
    
    Args:
        event_type: Type of lattice event
        data: Event data
    """
    try:
        from bridge_backend.genesis.bus import genesis_bus
        
        if not genesis_bus.is_enabled():
            logger.debug("[Umbra Genesis Link] Genesis bus disabled")
            return
        
        await genesis_bus.publish(f"umbra.lattice.{event_type}", {
            **data,
            "timestamp": datetime.now(UTC).isoformat()
        })
        
        logger.debug(f"[Umbra Genesis Link] Published: umbra.lattice.{event_type}")
        
    except ImportError:
        logger.debug("[Umbra Genesis Link] Genesis bus not available")
    except Exception as e:
        logger.error(f"[Umbra Genesis Link] Failed to publish: {e}")
