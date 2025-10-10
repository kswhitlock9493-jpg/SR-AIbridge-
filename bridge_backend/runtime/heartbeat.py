#!/usr/bin/env python3
"""
Heartbeat Ping System for SR-AIbridge v1.9.6d
Keeps Render dynos alive and verifies active connection
"""
import os, asyncio, logging
import httpx  # ensured in requirements
from urllib.parse import urlparse, urlunparse

logger = logging.getLogger(__name__)

_hb = os.getenv("HEARTBEAT_URL")
_render_external = os.getenv("RENDER_EXTERNAL_URL")  # Render injects this

def _auto_heartbeat_url():
    if _hb:
        return _hb
    base = _render_external
    if not base:
        return None
    # ensure /health path
    parsed = urlparse(base)
    hb = urlunparse(parsed._replace(path="/health"))
    logger.info(f"heartbeat: Auto-detected HEARTBEAT_URL={hb}")
    return hb

HEARTBEAT_URL = _auto_heartbeat_url()
HEARTBEAT_INTERVAL = int(os.getenv("HEARTBEAT_INTERVAL_SEC", "25"))

async def send_heartbeat():
    if not HEARTBEAT_URL:
        logger.info("heartbeat: no HEARTBEAT_URL set; skipping external ping")
        return
    payload = {
        "service": "sr-aibridge",
        "version": os.getenv("APP_VERSION", "v1.9.6d"),
        "stability": float(os.getenv("BRIDGE_STABILITY_SCORE", "100")),
    }
    try:
        async with httpx.AsyncClient(timeout=8) as client:
            await client.post(HEARTBEAT_URL, json=payload)
        logger.debug("heartbeat: sent")
    except Exception:
        # Quiet downgrade to internal checks; no repeated spam
        logger.warning("heartbeat: external ping failed; using internal monitor")

async def run():
    logger.info("heartbeat: ✅ initialized")
    while True:
        await send_heartbeat()
        await asyncio.sleep(HEARTBEAT_INTERVAL)
