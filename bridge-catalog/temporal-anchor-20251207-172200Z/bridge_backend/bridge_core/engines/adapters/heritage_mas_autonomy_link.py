"""
Heritage & MAS Autonomy Links
Connects Heritage agents and Multi-Agent System to Autonomy Engine via Genesis bus
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


async def register_heritage_mas_autonomy_links():
    """
    Register autonomy integration for Heritage subsystems and Multi-Agent System.
    Links agents, MAS coordination, and legacy heritage components.
    """
    from bridge_backend.genesis.bus import genesis_bus
    
    if not genesis_bus.is_enabled():
        logger.info("Genesis bus disabled, skipping heritage/MAS autonomy links")
        return
    
    logger.info("🔗 Registering Heritage & MAS → Autonomy links...")
    
    # MAS (Multi-Agent System) autonomy link
    async def handle_mas_event(event: Dict[str, Any]):
        """Handle MAS coordination events"""
        event_type = event.get("kind", "")
        
        # Agent failures trigger autonomy healing
        if "fail" in event_type.lower() or "error" in event_type.lower():
            await genesis_bus.publish("genesis.heal", {
                "type": "autonomy.mas_agent_failure",
                "source": "autonomy",
                "mas_event": event,
            })
        # Agent coordination goes to intent
        elif "coordination" in event_type.lower() or "task" in event_type.lower():
            await genesis_bus.publish("genesis.intent", {
                "type": "autonomy.mas_coordination",
                "source": "autonomy",
                "mas_event": event,
            })
        else:
            await genesis_bus.publish("genesis.fact", {
                "type": "autonomy.mas_event",
                "source": "autonomy",
                "mas_event": event,
            })
    
    # Heritage Agents autonomy link
    async def handle_heritage_agent_event(event: Dict[str, Any]):
        """Handle heritage agent events"""
        await genesis_bus.publish("genesis.intent", {
            "type": "autonomy.heritage_agent",
            "source": "autonomy",
            "heritage_event": event,
        })
    
    # Heritage Bridge autonomy link
    async def handle_heritage_bridge_event(event: Dict[str, Any]):
        """Handle heritage bridge events"""
        await genesis_bus.publish("genesis.intent", {
            "type": "autonomy.heritage_bridge",
            "source": "autonomy",
            "bridge_event": event,
        })
    
    # MAS Self-Healing autonomy link
    async def handle_mas_healing_event(event: Dict[str, Any]):
        """Handle MAS self-healing events"""
        # MAS healing events go directly to genesis.heal
        await genesis_bus.publish("genesis.heal", {
            "type": "autonomy.mas_self_heal",
            "source": "autonomy",
            "healing_event": event,
        })
    
    # Subscribe to heritage and MAS topics
    genesis_bus.subscribe("mas.agent", handle_mas_event)
    genesis_bus.subscribe("mas.coordination", handle_mas_event)
    genesis_bus.subscribe("mas.task", handle_mas_event)
    genesis_bus.subscribe("mas.failure", handle_mas_event)
    genesis_bus.subscribe("heritage.agent", handle_heritage_agent_event)
    genesis_bus.subscribe("heritage.bridge", handle_heritage_bridge_event)
    genesis_bus.subscribe("heal.events", handle_mas_healing_event)
    
    logger.info("✅ Heritage & MAS → Autonomy links registered")


async def publish_mas_event(event_type: str, data: Dict[str, Any]):
    """
    Utility function to publish MAS events from any agent.
    
    Args:
        event_type: Event type (agent, coordination, task, failure)
        data: Event data
    """
    try:
        from bridge_backend.genesis.bus import genesis_bus
        
        if genesis_bus.is_enabled():
            await genesis_bus.publish(f"mas.{event_type}", {
                **data,
                "timestamp": _get_timestamp()
            })
    except Exception as e:
        logger.debug(f"Failed to publish MAS event: {e}")


async def publish_heritage_agent_event(agent_id: str, action: str, details: Dict[str, Any] = None):
    """
    Utility function to publish heritage agent events.
    
    Args:
        agent_id: Agent identifier
        action: Action performed
        details: Additional details
    """
    try:
        from bridge_backend.genesis.bus import genesis_bus
        
        if genesis_bus.is_enabled():
            await genesis_bus.publish("heritage.agent", {
                "agent_id": agent_id,
                "action": action,
                "details": details or {},
                "timestamp": _get_timestamp()
            })
    except Exception as e:
        logger.debug(f"Failed to publish heritage agent event: {e}")


async def publish_heritage_bridge_event(event_type: str, data: Dict[str, Any]):
    """
    Utility function to publish heritage bridge events.
    
    Args:
        event_type: Event type
        data: Event data
    """
    try:
        from bridge_backend.genesis.bus import genesis_bus
        
        if genesis_bus.is_enabled():
            await genesis_bus.publish("heritage.bridge", {
                "event_type": event_type,
                **data,
                "timestamp": _get_timestamp()
            })
    except Exception as e:
        logger.debug(f"Failed to publish heritage bridge event: {e}")


def _get_timestamp() -> str:
    """Get ISO timestamp"""
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat() + "Z"
