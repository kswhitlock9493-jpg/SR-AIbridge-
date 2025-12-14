"""
Fault Injector for Heritage Bridge
Simplified version integrated with event bus
"""

import random
import logging
from typing import Dict, Any, Callable
from datetime import datetime, timezone
from ..event_bus import bus

logger = logging.getLogger(__name__)


class FaultInjector:
    """
    Fault injection for resilience testing
    Publishes fault events to the event bus
    """
    
    def __init__(self, base_write: Callable, 
                 corrupt_rate: float = 0.0,
                 delay_rate: float = 0.0,
                 reorder_rate: float = 0.0,
                 drop_rate: float = 0.0):
        self.base_write = base_write
        self.corrupt_rate = corrupt_rate
        self.delay_rate = delay_rate
        self.reorder_rate = reorder_rate
        self.drop_rate = drop_rate
        logger.info(f"💥 FaultInjector initialized (corrupt={corrupt_rate}, delay={delay_rate}, drop={drop_rate})")

    async def __call__(self, message: Dict[str, Any]):
        """Inject faults and write message"""
        fault_applied = None
        
        # Check for drop
        if random.random() < self.drop_rate:
            fault_applied = "drop"
            await bus.publish("fault.events", {
                "kind": "fault.drop",
                "message_id": message.get("task_id", "unknown"),
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            logger.warning(f"💥 Dropped message: {message.get('task_id')}")
            return  # Don't write
        
        # Check for corruption
        if random.random() < self.corrupt_rate:
            fault_applied = "corrupt"
            message = self._corrupt_message(message)
            await bus.publish("fault.events", {
                "kind": "fault.corrupt",
                "message_id": message.get("task_id", "unknown"),
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            logger.warning(f"💥 Corrupted message: {message.get('task_id')}")
        
        # Write (possibly corrupted) message
        self.base_write(message)
    
    def _corrupt_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Simple corruption - modify a random field"""
        msg = dict(message)
        if "payload" in msg and isinstance(msg["payload"], dict):
            msg["payload"]["_corrupted"] = True
        return msg
