#!/usr/bin/env python3
"""
Heartbeat Ping System for SR-AIbridge v1.9.5
Keeps Render dynos alive and verifies active connection
Includes self-healing and auto-repair capabilities
"""
import asyncio
import os
import logging
import importlib
import subprocess
import sys
import datetime
from typing import Optional

logger = logging.getLogger(__name__)

BRIDGE_BASE = os.getenv("BRIDGE_API_URL", "https://sr-aibridge.onrender.com")
HEARTBEAT_INTERVAL = 300  # 5 minutes


def record_repair(pkg: str, status: str):
    """Record repair attempts to persistent log for learning"""
    try:
        repair_log_path = os.path.join(os.path.dirname(__file__), ".bridge_repair_log")
        with open(repair_log_path, "a") as f:
            timestamp = datetime.datetime.utcnow().isoformat()
            f.write(f"[{timestamp}] {pkg}: {status}\n")
    except Exception as e:
        logger.warning(f"Could not write to repair log: {e}")


def ensure_httpx() -> bool:
    """
    Self-healing: ensure httpx is available, auto-install if missing
    Returns True if httpx is available, False otherwise
    """
    try:
        import httpx
        return True
    except ImportError:
        logger.warning("⚠️ httpx missing — initiating self-repair")
        try:
            # Auto-install httpx
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "httpx"],
                check=True,
                capture_output=True
            )
            # Invalidate import cache and retry
            importlib.invalidate_caches()
            import httpx
            record_repair("httpx", "auto-installed")
            logger.info("✅ httpx reinstalled and validated")
            return True
        except Exception as e:
            record_repair("httpx", f"repair_failed ({e})")
            logger.error(f"❌ httpx repair failed: {e}")
            return False


async def bridge_heartbeat():
    """
    Heartbeat ping system to keep Render dynos alive
    Runs continuously in the background
    Includes self-healing for missing dependencies
    """
    # Ensure httpx is available before starting
    if not ensure_httpx():
        logger.warning("⚠️ httpx not available and auto-repair failed, heartbeat disabled")
        return
    
    import httpx
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
