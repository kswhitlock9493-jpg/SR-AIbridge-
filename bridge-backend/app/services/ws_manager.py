"""
WebSocket manager service for SR-AIbridge
Handles WebSocket connections, broadcasting, and real-time updates
"""
import logging
import json
import asyncio
from datetime import datetime
from typing import Dict, List, Any
from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)

class WebSocketManager:
    """Enhanced WebSocket manager with connection tracking and broadcasting"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.connection_info: Dict[str, Dict] = {}
        self.message_history: List[Dict] = []
        self.broadcast_queue = asyncio.Queue()
        self.stats = {
            "total_connections": 0,
            "current_connections": 0,
            "messages_sent": 0,
            "messages_received": 0,
            "broadcasts": 0
        }
        
    async def connect(self, websocket: WebSocket, client_id: str = None) -> str:
        """Accept a WebSocket connection"""
        await websocket.accept()
        
        if not client_id:
            client_id = f"client_{len(self.active_connections)}_{int(datetime.utcnow().timestamp())}"
            
        self.active_connections[client_id] = websocket
        self.connection_info[client_id] = {
            "connected_at": datetime.utcnow(),
            "last_message": None,
            "message_count": 0
        }
        
        self.stats["total_connections"] += 1
        self.stats["current_connections"] = len(self.active_connections)
        
        logger.info(f"📡 WebSocket client connected: {client_id}")
        
        # Broadcast connection event
        await self.broadcast({
            "type": "client_connected",
            "client_id": client_id,
            "timestamp": datetime.utcnow().isoformat(),
            "total_clients": len(self.active_connections)
        })
        
        return client_id
        
    async def disconnect(self, client_id: str):
        """Disconnect a WebSocket client"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            del self.connection_info[client_id]
            
            self.stats["current_connections"] = len(self.active_connections)
            
            logger.info(f"📡 WebSocket client disconnected: {client_id}")
            
            # Broadcast disconnection event
            await self.broadcast({
                "type": "client_disconnected", 
                "client_id": client_id,
                "timestamp": datetime.utcnow().isoformat(),
                "total_clients": len(self.active_connections)
            })
            
    async def send_personal_message(self, message: dict, client_id: str):
        """Send a message to a specific client"""
        if client_id in self.active_connections:
            try:
                websocket = self.active_connections[client_id]
                await websocket.send_text(json.dumps(message))
                
                self.connection_info[client_id]["last_message"] = datetime.utcnow()
                self.connection_info[client_id]["message_count"] += 1
                self.stats["messages_sent"] += 1
                
                logger.debug(f"📡 Message sent to {client_id}: {message.get('type', 'unknown')}")
                
            except Exception as e:
                logger.error(f"📡 Error sending message to {client_id}: {e}")
                await self.disconnect(client_id)
                
    async def broadcast(self, message: dict, exclude_client: str = None):
        """Broadcast a message to all connected clients"""
        if not self.active_connections:
            return
            
        # Add timestamp if not present
        if "timestamp" not in message:
            message["timestamp"] = datetime.utcnow().isoformat()
            
        # Store in message history
        self.message_history.append({
            **message,
            "broadcast_at": datetime.utcnow(),
            "recipient_count": len(self.active_connections)
        })
        
        # Keep only last 100 messages
        if len(self.message_history) > 100:
            self.message_history = self.message_history[-100:]
            
        disconnected_clients = []
        
        for client_id, websocket in self.active_connections.items():
            if client_id == exclude_client:
                continue
                
            try:
                await websocket.send_text(json.dumps(message))
                
                self.connection_info[client_id]["last_message"] = datetime.utcnow()
                self.connection_info[client_id]["message_count"] += 1
                
            except Exception as e:
                logger.error(f"📡 Error broadcasting to {client_id}: {e}")
                disconnected_clients.append(client_id)
                
        # Clean up disconnected clients
        for client_id in disconnected_clients:
            await self.disconnect(client_id)
            
        self.stats["messages_sent"] += len(self.active_connections) - len(disconnected_clients)
        self.stats["broadcasts"] += 1
        
        logger.debug(f"📡 Broadcast sent to {len(self.active_connections)} clients: {message.get('type', 'unknown')}")
        
    async def handle_message(self, client_id: str, message: dict):
        """Handle incoming message from client"""
        self.stats["messages_received"] += 1
        self.connection_info[client_id]["last_message"] = datetime.utcnow()
        self.connection_info[client_id]["message_count"] += 1
        
        logger.debug(f"📡 Message received from {client_id}: {message.get('type', 'unknown')}")
        
        # Echo message back to all clients (including sender)
        await self.broadcast({
            "type": "client_message",
            "client_id": client_id,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        })
        
    def get_stats(self) -> Dict[str, Any]:
        """Get WebSocket statistics"""
        return {
            **self.stats,
            "active_clients": list(self.active_connections.keys()),
            "connection_details": {
                client_id: {
                    "connected_at": info["connected_at"].isoformat(),
                    "last_message": info["last_message"].isoformat() if info["last_message"] else None,
                    "message_count": info["message_count"]
                }
                for client_id, info in self.connection_info.items()
            },
            "recent_broadcasts": self.message_history[-10:]  # Last 10 broadcasts
        }
        
    async def send_system_update(self, update_type: str, data: dict):
        """Send system update to all clients"""
        await self.broadcast({
            "type": "system_update",
            "update_type": update_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        })
        
    async def send_agent_update(self, agent_data: dict):
        """Send agent status update"""
        await self.broadcast({
            "type": "agent_update",
            "agent": agent_data,
            "timestamp": datetime.utcnow().isoformat()
        })
        
    async def send_mission_update(self, mission_data: dict):
        """Send mission status update"""
        await self.broadcast({
            "type": "mission_update", 
            "mission": mission_data,
            "timestamp": datetime.utcnow().isoformat()
        })
        
    async def send_guardian_update(self, guardian_status: dict):
        """Send guardian daemon status update"""
        await self.broadcast({
            "type": "guardian_update",
            "guardian": guardian_status,
            "timestamp": datetime.utcnow().isoformat()
        })

# Global WebSocket manager instance
websocket_manager = WebSocketManager()