"""
WebSocket Connection Manager for SR-AIbridge

Handles real-time communication between backend and frontend clients.
Manages connection lifecycle, broadcasts, and message routing.
"""

import asyncio
import json
import logging
from typing import Dict, List, Set
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime

logger = logging.getLogger(__name__)

class ConnectionManager:
    """Manages WebSocket connections and broadcasting"""
    
    def __init__(self):
        # Active connections by connection ID
        self.active_connections: Dict[str, WebSocket] = {}
        # Connection metadata
        self.connection_info: Dict[str, Dict] = {}
        
    async def connect(self, websocket: WebSocket, client_id: str = None):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        
        # Generate client ID if not provided
        if not client_id:
            client_id = f"client_{len(self.active_connections)}_{datetime.now().timestamp()}"
        
        self.active_connections[client_id] = websocket
        self.connection_info[client_id] = {
            "connected_at": datetime.utcnow(),
            "last_ping": datetime.utcnow(),
            "subscriptions": set()
        }
        
        logger.info(f"🔌 WebSocket client {client_id} connected. Total connections: {len(self.active_connections)}")
        
        # Send connection confirmation
        await self.send_personal_message(client_id, {
            "type": "connection_established",
            "client_id": client_id,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return client_id
    
    def disconnect(self, client_id: str):
        """Remove a WebSocket connection"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            del self.connection_info[client_id]
            logger.info(f"🔌 WebSocket client {client_id} disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, client_id: str, message: dict):
        """Send a message to a specific client"""
        if client_id in self.active_connections:
            try:
                websocket = self.active_connections[client_id]
                await websocket.send_text(json.dumps(message, default=str))
            except Exception as e:
                logger.error(f"Error sending message to {client_id}: {e}")
                self.disconnect(client_id)
    
    async def broadcast(self, message: dict, exclude_client: str = None):
        """Broadcast a message to all connected clients"""
        if not self.active_connections:
            return
            
        message_str = json.dumps(message, default=str)
        disconnected_clients = []
        
        for client_id, websocket in self.active_connections.items():
            if client_id == exclude_client:
                continue
                
            try:
                await websocket.send_text(message_str)
            except WebSocketDisconnect:
                disconnected_clients.append(client_id)
            except Exception as e:
                logger.error(f"Error broadcasting to {client_id}: {e}")
                disconnected_clients.append(client_id)
        
        # Clean up disconnected clients
        for client_id in disconnected_clients:
            self.disconnect(client_id)
    
    async def subscribe(self, client_id: str, channel: str):
        """Subscribe a client to a specific channel"""
        if client_id in self.connection_info:
            self.connection_info[client_id]["subscriptions"].add(channel)
            await self.send_personal_message(client_id, {
                "type": "subscription_confirmed",
                "channel": channel
            })
    
    async def unsubscribe(self, client_id: str, channel: str):
        """Unsubscribe a client from a specific channel"""
        if client_id in self.connection_info:
            self.connection_info[client_id]["subscriptions"].discard(channel)
            await self.send_personal_message(client_id, {
                "type": "subscription_removed",
                "channel": channel
            })
    
    async def broadcast_to_channel(self, channel: str, message: dict):
        """Broadcast a message to clients subscribed to a specific channel"""
        if not self.active_connections:
            return
            
        message_str = json.dumps(message, default=str)
        disconnected_clients = []
        
        for client_id, websocket in self.active_connections.items():
            # Check if client is subscribed to this channel
            if channel not in self.connection_info.get(client_id, {}).get("subscriptions", set()):
                continue
                
            try:
                await websocket.send_text(message_str)
            except WebSocketDisconnect:
                disconnected_clients.append(client_id)
            except Exception as e:
                logger.error(f"Error broadcasting to channel {channel}, client {client_id}: {e}")
                disconnected_clients.append(client_id)
        
        # Clean up disconnected clients
        for client_id in disconnected_clients:
            self.disconnect(client_id)
    
    async def handle_message(self, client_id: str, message: dict):
        """Handle incoming messages from clients"""
        message_type = message.get("type")
        
        if message_type == "ping":
            # Update last ping time
            if client_id in self.connection_info:
                self.connection_info[client_id]["last_ping"] = datetime.utcnow()
            
            await self.send_personal_message(client_id, {
                "type": "pong",
                "timestamp": datetime.utcnow().isoformat()
            })
            
        elif message_type == "subscribe":
            channel = message.get("channel")
            if channel:
                await self.subscribe(client_id, channel)
                
        elif message_type == "unsubscribe":
            channel = message.get("channel")
            if channel:
                await self.unsubscribe(client_id, channel)
                
        elif message_type == "get_status":
            # Send current connection status
            await self.send_personal_message(client_id, {
                "type": "status",
                "connections": len(self.active_connections),
                "subscriptions": list(self.connection_info.get(client_id, {}).get("subscriptions", set()))
            })
    
    def get_stats(self):
        """Get connection statistics"""
        return {
            "total_connections": len(self.active_connections),
            "connection_details": [
                {
                    "client_id": client_id,
                    "connected_at": info["connected_at"].isoformat(),
                    "last_ping": info["last_ping"].isoformat(),
                    "subscriptions": list(info["subscriptions"])
                }
                for client_id, info in self.connection_info.items()
            ]
        }

# Global connection manager instance
websocket_manager = ConnectionManager()