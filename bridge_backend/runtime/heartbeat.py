#!/usr/bin/env python3
"""
Heartbeat Ping System for SR-AIbridge v1.9.4
Keeps Render dynos alive and verifies active connection
"""
import asyncio
import os
import logging
from typing import Optional

try:
    import httpx
except ImportError:
    httpx = None

logger = logging.getLogger(__name__)

BRIDGE_BASE = os.getenv("BRIDGE_API_URL", "https://sr-aibridge.onrender.com")
HEARTBEAT_INTERVAL = 300  # 5 minutes


async def bridge_heartbeat():
    """
    Heartbeat ping system to keep Render dynos alive
    Runs continuously in the background
    """
    if not httpx:
        logger.warning("⚠️ httpx not available, heartbeat disabled")
        return
    
    logger.info(f"💓 Starting heartbeat system (interval: {HEARTBEAT_INTERVAL}s)")
    
    while True:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{BRIDGE_BASE}/api/health")
                if response.status_code == 200:
                    logger.debug("💓 Heartbeat successful")
                else:
                    logger.warning(f"⚠️ Heartbeat returned status {response.status_code}")
        except Exception as e:
            logger.warning(f"⚠️ Heartbeat error: {e}")
        
        await asyncio.sleep(HEARTBEAT_INTERVAL)


async def start_heartbeat():
    """
    Start the heartbeat system as a background task
    """
    asyncio.create_task(bridge_heartbeat())
    logger.info("✅ Heartbeat system initialized")
