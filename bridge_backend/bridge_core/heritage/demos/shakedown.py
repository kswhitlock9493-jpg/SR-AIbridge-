"""
Shakedown Demo - System stress test
"""

import logging
import asyncio
from datetime import datetime, timezone
from ..event_bus import bus

logger = logging.getLogger(__name__)


async def run_shakedown():
    """
    Run shakedown demo - basic system stress test
    """
    logger.info("🚀 Starting shakedown demo...")
    
    # Publish start event
    await bus.publish("demo.events", {
        "kind": "demo.shakedown.start",
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    
    # Simulate various events
    events = [
        {"type": "task.created", "task_id": "shakedown-1"},
        {"type": "task.processing", "task_id": "shakedown-1"},
        {"type": "task.completed", "task_id": "shakedown-1"},
        {"type": "agent.status", "agent_id": "test-agent", "status": "active"},
        {"type": "system.health", "health_score": 0.95}
    ]
    
    for i, event in enumerate(events):
        await bus.publish("heritage.events", {
            "kind": "heritage.shakedown.event",
            "event_number": i + 1,
            "payload": event,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        await asyncio.sleep(0.5)
    
    # Publish completion
    await bus.publish("demo.events", {
        "kind": "demo.shakedown.complete",
        "events_processed": len(events),
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    
    logger.info("✅ Shakedown demo completed")
