"""
Federation Client for Heritage Bridge
Simplified federation with event bus integration
"""

import logging
from typing import Dict, Any, List
from datetime import datetime
from ..event_bus import bus

logger = logging.getLogger(__name__)


class FederationClient:
    """
    Simplified federation client integrated with event bus
    Handles task forwarding and heartbeat signaling
    """
    
    def __init__(self, node_id: str = "sr-bridge-main"):
        self.node_id = node_id
        self.connected_nodes = {}
        logger.info(f"🌐 FederationClient initialized (node={node_id})")

    async def forward_task(self, task_id: str, task_type: str, payload: Dict[str, Any], target_node: str = None):
        """Forward task to another bridge"""
        event = {
            "kind": "federation.task_forward",
            "task_id": task_id,
            "task_type": task_type,
            "payload": payload,
            "source_node": self.node_id,
            "target_node": target_node or "auto",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await bus.publish("federation.events", event)
        logger.info(f"📤 Task forwarded: {task_id} -> {target_node}")
        
        return {"status": "forwarded", "task_id": task_id}

    async def send_heartbeat(self, nodes: List[str] = None):
        """Send heartbeat to connected nodes"""
        event = {
            "kind": "federation.heartbeat",
            "node_id": self.node_id,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "online",
            "nodes": nodes or []
        }
        
        await bus.publish("federation.events", event)
        logger.debug(f"💓 Heartbeat sent from {self.node_id}")

    async def handle_ack(self, ack_data: Dict[str, Any]):
        """Handle acknowledgment from another node"""
        event = {
            "kind": "federation.ack",
            "payload": ack_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await bus.publish("federation.events", event)
        logger.debug(f"✅ ACK received: {ack_data.get('from_node')}")
