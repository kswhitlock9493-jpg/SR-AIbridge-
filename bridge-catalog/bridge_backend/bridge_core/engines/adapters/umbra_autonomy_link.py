"""
Umbra Triage Mesh - Autonomy Link Adapter
Integrates with Autonomy Engine for auto-heal execution
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


async def execute_autonomy_heal(heal_intent: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute healing via Autonomy Engine
    
    Args:
        heal_intent: Heal intent details including action, target, parameters
        
    Returns:
        Execution result
    """
    try:
        from bridge_backend.engines.autonomy.core import AutonomyEngine
        
        autonomy = AutonomyEngine()
        
        # Execute heal via autonomy
        result = await autonomy.auto_heal(heal_intent)
        
        if result.get("success"):
            logger.info(f"[Umbra Autonomy Link] Heal executed successfully: {heal_intent.get('action')}")
        else:
            logger.warning(f"[Umbra Autonomy Link] Heal failed: {result.get('reason')}")
        
        return {
            "ok": result.get("success", False),
            "result": result
        }
    
    except ImportError:
        logger.warning("[Umbra Autonomy Link] Autonomy engine not available")
        return {
            "ok": False,
            "reason": "autonomy_engine_unavailable"
        }
    except Exception as e:
        logger.error(f"[Umbra Autonomy Link] Autonomy heal error: {e}")
        return {
            "ok": False,
            "error": str(e)
        }


async def emit_heal_intent(plan_id: str, ticket_id: str, actions: list):
    """
    Emit heal intent to Genesis bus for Autonomy to process
    
    Args:
        plan_id: Heal plan ID
        ticket_id: Ticket ID
        actions: List of heal actions
    """
    try:
        from bridge_backend.genesis.bus import genesis_bus
        
        if not genesis_bus.is_enabled():
            return
        
        await genesis_bus.publish("triage.heal.intent", {
            "plan_id": plan_id,
            "ticket_id": ticket_id,
            "actions": actions,
            "source": "umbra_triage"
        })
        
        logger.info(f"[Umbra Autonomy Link] Emitted heal intent: {plan_id}")
    
    except Exception as e:
        logger.warning(f"[Umbra Autonomy Link] Failed to emit heal intent: {e}")


async def emit_heal_applied(plan_id: str, ticket_id: str, result: Dict[str, Any]):
    """
    Emit heal applied event after successful execution
    
    Args:
        plan_id: Heal plan ID
        ticket_id: Ticket ID
        result: Execution result
    """
    try:
        from bridge_backend.genesis.bus import genesis_bus
        
        if not genesis_bus.is_enabled():
            return
        
        await genesis_bus.publish("triage.heal.applied", {
            "plan_id": plan_id,
            "ticket_id": ticket_id,
            "result": result,
            "source": "umbra_triage"
        })
        
        logger.info(f"[Umbra Autonomy Link] Emitted heal applied: {plan_id}")
    
    except Exception as e:
        logger.warning(f"[Umbra Autonomy Link] Failed to emit heal applied: {e}")


async def emit_heal_rollback(plan_id: str, ticket_id: str, reason: str):
    """
    Emit heal rollback event
    
    Args:
        plan_id: Heal plan ID
        ticket_id: Ticket ID
        reason: Rollback reason
    """
    try:
        from bridge_backend.genesis.bus import genesis_bus
        
        if not genesis_bus.is_enabled():
            return
        
        await genesis_bus.publish("triage.heal.rollback", {
            "plan_id": plan_id,
            "ticket_id": ticket_id,
            "reason": reason,
            "source": "umbra_triage"
        })
        
        logger.warning(f"[Umbra Autonomy Link] Emitted heal rollback: {plan_id} - {reason}")
    
    except Exception as e:
        logger.warning(f"[Umbra Autonomy Link] Failed to emit heal rollback: {e}")


async def subscribe_to_autonomy_events():
    """
    Subscribe to Autonomy events that might affect triage
    """
    try:
        from bridge_backend.genesis.bus import genesis_bus
        
        if not genesis_bus.is_enabled():
            return
        
        # Subscribe to autonomy heal events
        await genesis_bus.subscribe("autonomy.heal.applied", on_autonomy_heal_applied)
        await genesis_bus.subscribe("autonomy.heal.error", on_autonomy_heal_error)
        
        logger.info("[Umbra Autonomy Link] Subscribed to autonomy events")
    
    except Exception as e:
        logger.error(f"[Umbra Autonomy Link] Failed to subscribe to events: {e}")


async def on_autonomy_heal_applied(event: Dict[str, Any]):
    """Handle autonomy heal applied event"""
    try:
        logger.info(f"[Umbra Autonomy Link] Autonomy heal applied: {event.get('action')}")
        # Could update triage tickets based on autonomy heals
    except Exception as e:
        logger.error(f"[Umbra Autonomy Link] Failed to handle heal applied: {e}")


async def on_autonomy_heal_error(event: Dict[str, Any]):
    """Handle autonomy heal error event"""
    try:
        logger.warning(f"[Umbra Autonomy Link] Autonomy heal error: {event.get('reason')}")
        # Could create new triage ticket for failed autonomy heal
    except Exception as e:
        logger.error(f"[Umbra Autonomy Link] Failed to handle heal error: {e}")
