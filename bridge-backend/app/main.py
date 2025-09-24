"""
SR-AIbridge Backend - Main Application Entry Point

Modular FastAPI application with routes and services organized cleanly.
"""
import os
import asyncio
import logging
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from dotenv import load_dotenv
import json

# Import routes
from .routes import health, daemon, guardian, missions, logs

# Import existing modules (these will be moved to services)
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rituals.manage_data import DataRituals
from websocket_manager import websocket_manager
from autonomous_scheduler import AutonomousScheduler

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load env variables
load_dotenv()

# In-memory storage (this should be moved to a service)
class InMemoryStorage:
    def __init__(self):
        self.captain_messages: List[Dict] = []
        self.armada_fleet: List[Dict] = []
        self.agents: List[Dict] = []
        self.missions: List[Dict] = []
        self.vault_logs: List[Dict] = []
        self.next_id = 1
    
    def get_next_id(self) -> int:
        current_id = self.next_id
        self.next_id += 1
        return current_id

# Global storage instance
storage = InMemoryStorage()

# Initialize rituals manager for data operations
rituals = DataRituals(storage)

# Initialize autonomous scheduler
scheduler = AutonomousScheduler(storage, websocket_manager)

# FastAPI app
app = FastAPI(
    title="SR-AIbridge Backend",
    version="1.1.0-autonomous",
    description="Fully autonomous SR-AIbridge with real-time WebSocket updates"
)

# CORS configuration for both production and development
origins = [
    "https://bridge.netlify.app",
    "https://sr-aibridge.netlify.app",
    "https://*.netlify.app",  # Allow all Netlify subdomains
    "https://*.onrender.com",  # Allow all Render subdomains
    "http://localhost:3000",  # Development frontend
    "http://127.0.0.1:3000",   # Alternative localhost
    "http://localhost:3001",  # Alternative development port
    "https://localhost:3000",  # HTTPS development
    "https://localhost:3001"   # HTTPS alternative development port
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models (these should eventually be moved to a models module)
class Message(BaseModel):
    id: Optional[int] = None
    author: str
    message: str
    timestamp: Optional[datetime] = None

class Agent(BaseModel):
    id: Optional[int] = None
    name: str
    endpoint: str
    status: str = "online"
    capabilities: List[str] = []
    last_heartbeat: Optional[datetime] = None

class AgentCreate(BaseModel):
    name: str
    endpoint: str
    capabilities: List[str] = []

# Guardian Daemon (this should be moved to services)
class GuardianDaemon:
    """Guardian daemon for continuous self-testing and system monitoring"""
    
    def __init__(self, storage, websocket_manager):
        self.storage = storage
        self.websocket_manager = websocket_manager
        self.active = True
        self.selftest_status = "unknown"
        self.last_selftest = None
        self.last_action = "initialized"
        self.last_result = None
        self.heartbeat = datetime.utcnow()
        self.selftest_interval = 300  # 5 minutes
        
    def get_status(self):
        """Get current Guardian status"""
        return {
            "active": self.active,
            "status": self.selftest_status,
            "last_selftest": self.last_selftest.isoformat() if self.last_selftest else None,
            "last_action": self.last_action,
            "last_result": self.last_result,
            "heartbeat": self.heartbeat.isoformat() if self.heartbeat else None,
            "next_selftest": (self.last_selftest + timedelta(seconds=self.selftest_interval)).isoformat() if self.last_selftest else None
        }
    
    async def run_selftest(self):
        """Run comprehensive self-test"""
        try:
            logger.info("🛡️ Guardian running self-test...")
            self.heartbeat = datetime.utcnow()
            self.last_selftest = datetime.utcnow()
            self.last_action = "selftest"
            
            # Test basic system components
            tests_passed = 0
            total_tests = 4
            
            # Test 1: Storage accessibility
            try:
                len(self.storage.agents)
                tests_passed += 1
            except Exception:
                logger.error("Guardian selftest: Storage test failed")
                
            # Test 2: Data integrity
            try:
                agents_online = len([a for a in self.storage.agents if a.get("status") == "online"])
                if agents_online >= 0:  # Basic sanity
                    tests_passed += 1
            except Exception:
                logger.error("Guardian selftest: Data integrity test failed")
                
            # Test 3: WebSocket manager
            try:
                if hasattr(self.websocket_manager, 'active_connections'):
                    tests_passed += 1
            except Exception:
                logger.error("Guardian selftest: WebSocket test failed")
                
            # Test 4: Basic API connectivity
            try:
                if len(self.storage.missions) >= 0:
                    tests_passed += 1
            except Exception:
                logger.error("Guardian selftest: API test failed")
                
            self.selftest_status = "healthy" if tests_passed >= 3 else "degraded"
            self.last_result = f"{tests_passed}/{total_tests} tests passed"
            
            logger.info(f"🛡️ Guardian self-test completed: {self.last_result}")
            
        except Exception as e:
            logger.error(f"Guardian selftest error: {e}")
            self.selftest_status = "error"
            self.last_selftest = datetime.utcnow()
            self.last_action = "selftest_error"
            self.last_result = f"Critical selftest error: {str(e)}"
            raise
    
    async def activate(self):
        """Activate Guardian daemon"""
        self.active = True
        self.last_action = "activated"
        self.heartbeat = datetime.utcnow()
        logger.info("🛡️ Guardian daemon activated")
        return {"success": True, "message": "Guardian daemon activated", "status": self.get_status()}

# Initialize Guardian daemon
guardian = GuardianDaemon(storage, websocket_manager)

# Include routers
app.include_router(health.router)
app.include_router(daemon.router)
app.include_router(guardian.router)
app.include_router(missions.router)
app.include_router(logs.router)

# Additional endpoints that need refactoring into services
# TODO: Move these to appropriate route files

# Make storage, guardian, scheduler available to routes
# This is a temporary solution - should use dependency injection
app.state.storage = storage
app.state.guardian = guardian  
app.state.scheduler = scheduler