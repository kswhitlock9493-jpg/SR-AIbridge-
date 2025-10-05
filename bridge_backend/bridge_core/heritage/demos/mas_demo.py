"""
MAS Demo - Multi-Agent System healing demonstration
"""

import logging
import asyncio
from datetime import datetime
from ..event_bus import bus
from ..mas.adapters import BridgeMASAdapter, SelfHealingMASAdapter
from ..mas.fault_injector import FaultInjector

logger = logging.getLogger(__name__)


async def run_mas():
    """
    Run MAS healing demo
    Demonstrates fault injection and self-healing
    """
    logger.info("🚀 Starting MAS healing demo...")
    
    # Publish start event
    await bus.publish("demo.events", {
        "kind": "demo.mas.start",
        "timestamp": datetime.utcnow().isoformat()
    })
    
    # Create MAS components
    log = []
    
    def write_log(msg):
        log.append(msg)
    
    # Create adapter with fault injection
    fault_injector = FaultInjector(
        base_write=write_log,
        corrupt_rate=0.3,
        drop_rate=0.1
    )
    
    mas_adapter = BridgeMASAdapter(order_write=write_log)
    healing_adapter = SelfHealingMASAdapter(mas_adapter, retry_delay=0.1, max_retries=2)
    
    # Send test messages
    test_messages = [
        {"event_type": "task.start", "task_id": "mas-1", "timestamp": datetime.utcnow().isoformat()},
        {"event_type": "task.progress", "task_id": "mas-1", "timestamp": datetime.utcnow().isoformat()},
        {"event_type": "task.complete", "task_id": "mas-1", "timestamp": datetime.utcnow().isoformat()},
        {"bad": "message"},  # This will trigger healing
    ]
    
    for i, msg in enumerate(test_messages):
        await fault_injector(msg)
        await healing_adapter.handle_incoming(msg)
        
        await bus.publish("heritage.events", {
            "kind": "heritage.mas.message",
            "message_number": i + 1,
            "message": msg,
            "log_size": len(log),
            "timestamp": datetime.utcnow().isoformat()
        })
        
        await asyncio.sleep(0.3)
    
    # Publish completion
    await bus.publish("demo.events", {
        "kind": "demo.mas.complete",
        "messages_processed": len(test_messages),
        "log_entries": len(log),
        "timestamp": datetime.utcnow().isoformat()
    })
    
    logger.info("✅ MAS healing demo completed")
