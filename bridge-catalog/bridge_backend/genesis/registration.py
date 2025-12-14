"""
Genesis Registration for Embedded Autonomy Node
v1.9.7n

This module registers the Embedded Autonomy Node with the Genesis Bus,
ensuring it's recognized as a certified micro-Bridge in the federation.
"""
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


def register_embedded_nodes() -> Dict[str, Any]:
    """
    Register the Embedded Autonomy Node with Genesis Bus
    
    Returns:
        Dictionary containing registration status and node information
    """
    node = {
        "engine": "autonomy_node",
        "location": ".github/autonomy_node",
        "status": "active",
        "type": "micro_bridge",
        "certified": True,
        "version": "1.9.7n"
    }
    
    try:
        # Import Genesis bus only when needed to avoid circular dependencies
        from bridge_backend.genesis.bus import genesis_bus
        
        if genesis_bus.is_enabled():
            logger.info("🧠 Registering Embedded Autonomy Node with Genesis Bus.")
            
            # Publish registration event asynchronously
            import asyncio
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # Publish the registration event
            loop.run_until_complete(
                genesis_bus.publish("genesis.node.register", node)
            )
            
            logger.info("✅ Embedded Autonomy Node registered successfully.")
            return {"registered": True, "node": node}
        else:
            logger.warning("⚠️ Genesis Bus not enabled, skipping node registration.")
            return {"registered": False, "reason": "genesis_disabled", "node": node}
            
    except ImportError as e:
        logger.warning(f"⚠️ Could not import Genesis Bus: {e}")
        return {"registered": False, "reason": "import_error", "node": node}
    except Exception as e:
        logger.error(f"❌ Failed to register Embedded Autonomy Node: {e}")
        return {"registered": False, "reason": str(e), "node": node}
