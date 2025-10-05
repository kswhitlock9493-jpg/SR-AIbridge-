"""
Federation Demo - Cross-bridge communication
"""

import logging
import asyncio
from datetime import datetime
from ..event_bus import bus
from ..federation.federation_client import FederationClient

logger = logging.getLogger(__name__)


async def run_federation():
    """
    Run federation demo
    Demonstrates task forwarding and heartbeats
    """
    logger.info("🚀 Starting federation demo...")
    
    # Publish start event
    await bus.publish("demo.events", {
        "kind": "demo.federation.start",
        "timestamp": datetime.utcnow().isoformat()
    })
    
    # Create federation client
    fed_client = FederationClient(node_id="demo-bridge-main")
    
    # Simulate federation operations
    operations = [
        ("heartbeat", None),
        ("forward_task", {"task_id": "fed-1", "task_type": "analysis", "payload": {"data": "test"}}),
        ("heartbeat", None),
        ("forward_task", {"task_id": "fed-2", "task_type": "processing", "payload": {"data": "test2"}}),
        ("ack", {"from_node": "demo-bridge-remote", "task_id": "fed-1"}),
    ]
    
    for i, (op_type, op_data) in enumerate(operations):
        if op_type == "heartbeat":
            await fed_client.send_heartbeat(["demo-bridge-remote"])
        elif op_type == "forward_task":
            await fed_client.forward_task(**op_data)
        elif op_type == "ack":
            await fed_client.handle_ack(op_data)
        
        await bus.publish("heritage.events", {
            "kind": "heritage.federation.operation",
            "operation_number": i + 1,
            "operation_type": op_type,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        await asyncio.sleep(0.5)
    
    # Publish completion
    await bus.publish("demo.events", {
        "kind": "demo.federation.complete",
        "operations_completed": len(operations),
        "timestamp": datetime.utcnow().isoformat()
    })
    
    logger.info("✅ Federation demo completed")
