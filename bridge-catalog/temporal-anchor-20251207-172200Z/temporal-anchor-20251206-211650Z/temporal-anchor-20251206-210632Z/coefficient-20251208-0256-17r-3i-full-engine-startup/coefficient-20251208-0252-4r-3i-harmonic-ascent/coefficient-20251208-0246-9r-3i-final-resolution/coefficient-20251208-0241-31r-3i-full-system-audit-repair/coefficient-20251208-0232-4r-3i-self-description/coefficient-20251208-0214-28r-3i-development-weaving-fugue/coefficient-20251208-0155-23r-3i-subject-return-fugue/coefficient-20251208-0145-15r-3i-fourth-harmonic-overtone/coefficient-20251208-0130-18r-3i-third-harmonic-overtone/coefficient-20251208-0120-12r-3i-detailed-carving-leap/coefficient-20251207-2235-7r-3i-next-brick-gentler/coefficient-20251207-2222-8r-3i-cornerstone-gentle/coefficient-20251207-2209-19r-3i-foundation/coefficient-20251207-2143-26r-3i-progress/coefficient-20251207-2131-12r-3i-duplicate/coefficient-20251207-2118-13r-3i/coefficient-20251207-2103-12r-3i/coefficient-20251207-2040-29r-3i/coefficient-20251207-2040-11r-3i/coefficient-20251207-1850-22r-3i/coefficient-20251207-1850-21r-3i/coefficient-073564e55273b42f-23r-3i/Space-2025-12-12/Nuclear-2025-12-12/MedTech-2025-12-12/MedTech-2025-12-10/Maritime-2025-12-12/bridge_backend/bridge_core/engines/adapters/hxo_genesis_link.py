"""
HXO Genesis Link Adapter
Connects HXO to Genesis event bus for unified orchestration
v1.9.6q - Async-safe implementation with tolerant sync/async bus methods
"""

from __future__ import annotations
import logging
from typing import Optional
from ...utils.async_tools import maybe_await, retry_async

logger = logging.getLogger(__name__)

class HXOGenesisLink:
    _registered: bool = False

    def __init__(self, bus, hxo):
        self.bus = bus
        self.hxo = hxo

    async def register(self) -> None:
        if self._registered:
            logger.debug("[HXO Genesis Link] Already registered; skipping.")
            return

        async def _do_register():
            # subscribe may be sync or async depending on bus impl
            await maybe_await(self.bus.subscribe("genesis.heal", self._on_heal))
            await maybe_await(self.bus.subscribe("deploy.tde.orchestrator.completed", self._on_tde_done))
            await maybe_await(self.bus.subscribe("deploy.tde.orchestrator.failed", self._on_tde_failed))

            # optional announce hook on the bus (could be sync)
            announce = getattr(self.bus, "announce_component", None)
            if announce:
                await maybe_await(announce("hxo"))

        try:
            await retry_async(_do_register, attempts=6, base_delay=0.2)
            self._registered = True
            logger.info("[HXO Genesis Link] ✅ Registration established")
        except Exception as e:  # noqa: BLE001
            logger.error("[HXO Genesis Link] Registration failed: %s", e)
            raise

    async def _on_heal(self, event: dict) -> None:
        # fan-in to HXO orchestration entry
        await maybe_await(self.hxo.handle_genesis_heal(event))

    async def _on_tde_done(self, event: dict) -> None:
        await maybe_await(self.hxo.on_tde_completed(event))

    async def _on_tde_failed(self, event: dict) -> None:
        await maybe_await(self.hxo.on_tde_failed(event))


# Legacy function-based API for backward compatibility
async def register_hxo_genesis_link():
    """
    Register HXO with Genesis event bus.
    Subscribes to relevant topics and publishes HXO schema.
    
    DEPRECATED: Use HXOGenesisLink class instead.
    This function is kept for backward compatibility with existing code.
    """
    try:
        from bridge_backend.genesis.bus import genesis_bus
        
        if not genesis_bus.is_enabled():
            logger.info("[HXO Genesis Link] Genesis bus disabled, skipping registration")
            return
        
        # Subscribe to healing topics
        await maybe_await(genesis_bus.subscribe("genesis.heal", _on_heal_request))
        
        # Subscribe to autonomy signals
        await maybe_await(genesis_bus.subscribe("genesis.intent", _on_autonomy_intent))
        
        # Subscribe to new v1.9.6p topics
        await maybe_await(genesis_bus.subscribe("hxo.link.autonomy", _on_autonomy_link))
        await maybe_await(genesis_bus.subscribe("hxo.link.cascade", _on_cascade_link))
        await maybe_await(genesis_bus.subscribe("hxo.link.leviathan", _on_leviathan_link))
        
        # Publish HXO schema
        await genesis_bus.publish("genesis.echo", {
            "type": "engine.registered",
            "engine": "hxo",
            "version": "1.9.6q",
            "capabilities": [
                "adaptive_sharding",
                "content_addressed_dedup",
                "merkle_aggregation",
                "idempotent_execution",
                "resumable_checkpoints",
                "backpressure_control",
                "self_healing",
                "predictive_orchestration",
                "temporal_event_replay",
                "zero_downtime_upgrade",
                "quantum_entropy_hashing",
                "harmonic_consensus_protocol",
                "cross_federation_telemetry",
                "adaptive_load_routing",
                "auto_heal_cascade"
            ]
        })
        
        logger.info("✅ [HXO Genesis Link] Registered with Genesis bus")
        
    except ImportError as e:
        logger.warning(f"[HXO Genesis Link] Genesis bus not available: {e}")
    except Exception as e:
        logger.error(f"[HXO Genesis Link] Registration failed: {e}")


async def _on_heal_request(event: dict):
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


async def _on_autonomy_intent(event: dict):
    """Handle autonomy intents that might affect HXO"""
    try:
        intent_type = event.get("type")
        
        if intent_type == "autotune.request":
            # Autonomy is requesting auto-tuning
            logger.info("[HXO Genesis Link] Received autotune intent from Autonomy")
            # Could trigger shard rebalancing, etc.
        
    except Exception as e:
        logger.error(f"[HXO Genesis Link] Autonomy intent handler failed: {e}")


async def _on_autonomy_link(event: dict):
    """Handle autonomy link events for HXO"""
    try:
        logger.debug(f"[HXO Genesis Link] Autonomy link event: {event.get('type', 'unknown')}")
    except Exception as e:
        logger.error(f"[HXO Genesis Link] Autonomy link handler failed: {e}")


async def _on_cascade_link(event: dict):
    """Handle cascade link events for HXO orchestration"""
    try:
        logger.debug(f"[HXO Genesis Link] Cascade link event: {event.get('type', 'unknown')}")
    except Exception as e:
        logger.error(f"[HXO Genesis Link] Cascade link handler failed: {e}")


async def _on_leviathan_link(event: dict):
    """Handle Leviathan predictive orchestration events"""
    try:
        logger.debug(f"[HXO Genesis Link] Leviathan link event: {event.get('type', 'unknown')}")
    except Exception as e:
        logger.error(f"[HXO Genesis Link] Leviathan link handler failed: {e}")


async def publish_hxo_event(topic: str, event: dict):
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

