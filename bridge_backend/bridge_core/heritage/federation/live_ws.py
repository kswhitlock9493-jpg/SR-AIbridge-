"""
Live WebSocket server for Heritage Bridge
Bridge-local WebSocket for real-time event streaming
"""

import logging
from typing import Set
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime, timezone
from ..event_bus import bus

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manage WebSocket connections"""
    
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
    
    async def connect(self, websocket: WebSocket):
        """Accept new WebSocket connection"""
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"🔌 WebSocket connected (total: {len(self.active_connections)})")
    
    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection"""
        self.active_connections.discard(websocket)
        logger.info(f"🔌 WebSocket disconnected (total: {len(self.active_connections)})")
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connections"""
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"❌ Broadcast error: {e}")
                self.disconnect(connection)


# Global manager instance
manager = ConnectionManager()


async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time event streaming"""
    await manager.connect(websocket)
    
    try:
        while True:
            # Receive messages from client
            data = await websocket.receive_json()
            
            # Handle client commands
            if data.get("type") == "fault.config":
                # Client wants to configure fault injection
                await bus.publish("fault.events", {
                    "kind": "fault.config",
                    "config": data.get("cfg", {}),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
            
            elif data.get("type") == "demo.start":
                # Client wants to start a demo
                await bus.publish("demo.events", {
                    "kind": "demo.start",
                    "mode": data.get("mode"),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"❌ WebSocket error: {e}")
        manager.disconnect(websocket)


# Subscribe to event bus topics and broadcast to WebSocket clients
def _broadcast_handler(event: dict):
    """Handler to broadcast bus events to WebSocket clients"""
    import asyncio
    asyncio.create_task(manager.broadcast(event))


# Register broadcast handlers for key topics
bus.subscribe("heritage.events", _broadcast_handler)
bus.subscribe("bridge.events", _broadcast_handler)
bus.subscribe("heal.events", _broadcast_handler)
bus.subscribe("fault.events", _broadcast_handler)
bus.subscribe("federation.events", _broadcast_handler)
bus.subscribe("anchor.events", _broadcast_handler)
bus.subscribe("metrics.update", _broadcast_handler)
