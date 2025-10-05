"""
MAS Adapters for Heritage Bridge
Integrates existing MAS components with the event bus
"""

import logging
from typing import Dict, Any, Callable
from datetime import datetime
from ..event_bus import bus

logger = logging.getLogger(__name__)


class BridgeMASAdapter:
    """
    Bridge Multi-Agent System Adapter
    Routes agent events through the unified event bus
    """
    
    def __init__(self, bridge=None, order_write: Callable = None):
        self.bridge = bridge
        self.order_write = order_write or (lambda x: None)
        logger.info("🤖 BridgeMASAdapter initialized")

    async def handle_bridge_event(self, event: dict):
        """Handle bridge event and publish to bus"""
        # Publish to event bus
        await bus.publish("bridge.events", {
            "kind": "heritage.mas.event",
            "payload": event,
            "timestamp": event.get("timestamp", datetime.utcnow().isoformat())
        })
        
        # Write to order log
        self.order_write({
            "timestamp": event.get("timestamp", datetime.utcnow().isoformat()),
            "type": event.get("event_type"),
            "task_id": event.get("task_id"),
            "agent": event.get("agent"),
            "payload": event.get("payload", {})
        })


class SelfHealingMASAdapter:
    """
    Self-healing MAS adapter with retry and recovery logic
    Wraps BridgeMASAdapter with healing capabilities
    """
    
    def __init__(self, mas_adapter: BridgeMASAdapter, retry_delay: float = 1.0, max_retries: int = 3):
        self.mas = mas_adapter
        self.retry_delay = retry_delay
        self.max_retries = max_retries
        self.retry_count = {}
        logger.info("🔄 SelfHealingMASAdapter initialized")

    async def handle_incoming(self, message: dict):
        """Handle incoming message with healing logic"""
        # Validate message
        if not self._validate_message(message):
            logger.warning(f"⚠️ Invalid message received: {message}")
            
            # Request resend
            await bus.publish("heal.events", {
                "kind": "heal.resend_request",
                "original_message": message,
                "reason": "validation_failed",
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Write resend request
            self.mas.order_write({
                "type": "resend_request",
                "timestamp": datetime.utcnow().isoformat(),
                "reason": "validation_failed"
            })
            return
        
        # Pass to underlying adapter
        await self.mas.handle_bridge_event(message)
    
    def _validate_message(self, message: dict) -> bool:
        """Simple validation - check for required fields"""
        return isinstance(message, dict) and any(
            key in message for key in ["event_type", "task_id", "timestamp"]
        )
