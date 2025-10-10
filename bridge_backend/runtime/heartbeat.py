#!/usr/bin/env python3
"""
Heartbeat Ping System for SR-AIbridge v1.9.6b
Keeps Render dynos alive and verifies active connection
"""
import os, asyncio, logging
import httpx  # ensured in requirements

logger = logging.getLogger(__name__)
HEARTBEAT_URL = os.getenv("HEARTBEAT_URL")  # optional
HEARTBEAT_INTERVAL = int(os.getenv("HEARTBEAT_INTERVAL_SEC", "25"))

async def send_heartbeat():
    if not HEARTBEAT_URL:
        logger.info("heartbeat: no HEARTBEAT_URL set; skipping external ping")
        return
    payload = {
        "service": "sr-aibridge",
        "version": os.getenv("APP_VERSION", "v1.9.6b"),
        "stability": float(os.getenv("BRIDGE_STABILITY_SCORE", "100")),
    }
    try:
        async with httpx.AsyncClient(timeout=8) as client:
            await client.post(HEARTBEAT_URL, json=payload)
        logger.debug("heartbeat: sent")
    except Exception as e:
        logger.warning(f"heartbeat: failed: {e!r}")

async def run():
    logger.info("heartbeat: ✅ initialized")
    while True:
        await send_heartbeat()
        await asyncio.sleep(HEARTBEAT_INTERVAL)
