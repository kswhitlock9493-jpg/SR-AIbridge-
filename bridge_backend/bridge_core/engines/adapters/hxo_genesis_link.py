"""
HXO Genesis Link Adapter
Connects HXO to Genesis event bus for unified orchestration
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


async def register_hxo_genesis_link():
    """
    Register HXO with Genesis event bus.
    Subscribes to relevant topics and publishes HXO schema.
    """
    try:
        from bridge_backend.genesis.bus import genesis_bus
        
        if not genesis_bus.is_enabled():
            logger.info("[HXO Genesis Link] Genesis bus disabled, skipping registration")
            return
        
        # Subscribe to healing topics
        await genesis_bus.subscribe("genesis.heal", _on_heal_request)
        
        # Subscribe to autonomy signals
        await genesis_bus.subscribe("genesis.intent", _on_autonomy_intent)
        
        # Publish HXO schema
        await genesis_bus.publish("genesis.echo", {
            "type": "engine.registered",
            "engine": "hxo",
            "version": "1.9.6n",
            "capabilities": [
                "adaptive_sharding",
                "content_addressed_dedup",
                "merkle_aggregation",
                "idempotent_execution",
                "resumable_checkpoints",
                "backpressure_control",
                "self_healing"
            ]
        })
        
        logger.info("✅ [HXO Genesis Link] Registered with Genesis bus")
        
    except ImportError as e:
        logger.warning(f"[HXO Genesis Link] Genesis bus not available: {e}")
    except Exception as e:
        logger.error(f"[HXO Genesis Link] Registration failed: {e}")


async def _on_heal_request(event: Dict[str, Any]):
    """Handle healing requests from Autonomy"""
    try:
        plan_id = event.get("plan_id")
        if not plan_id:
            return
        
        logger.info(f"[HXO Genesis Link] Received heal request for plan {plan_id}")
        
        # In a full implementation, this would trigger plan recovery/replay
        # For now, just log
        
    except Exception as e:
        logger.error(f"[HXO Genesis Link] Heal request handler failed: {e}")


async def _on_autonomy_intent(event: Dict[str, Any]):
    """Handle autonomy intents that might affect HXO"""
    try:
        intent_type = event.get("type")
        
        if intent_type == "autotune.request":
            # Autonomy is requesting auto-tuning
            logger.info("[HXO Genesis Link] Received autotune intent from Autonomy")
            # Could trigger shard rebalancing, etc.
        
    except Exception as e:
        logger.error(f"[HXO Genesis Link] Autonomy intent handler failed: {e}")


async def publish_hxo_event(topic: str, event: Dict[str, Any]):
    """
    Publish HXO event to Genesis bus.
    
    Args:
        topic: Genesis topic
        event: Event payload
    """
    try:
        from bridge_backend.genesis.bus import genesis_bus
        
        if genesis_bus.is_enabled():
            await genesis_bus.publish(topic, event)
        
    except ImportError:
        logger.debug("[HXO Genesis Link] Genesis bus not available")
    except Exception as e:
        logger.error(f"[HXO Genesis Link] Failed to publish event: {e}")
