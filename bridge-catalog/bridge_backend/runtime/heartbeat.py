import asyncio
import httpx
import os
import logging
import socket
import time
from datetime import datetime

# Initialize logger
logger = logging.getLogger(__name__)

async def start_heartbeat():
    """
    Wait until DNS for the Cloudflare tunnel resolves before starting heartbeat
    """
    tunnel_host = os.getenv("GENESIS_API_URL", "").replace("https://", "")
    logger.info(f"🌍 Waiting for DNS resolution of {tunnel_host}")

    start_time = time.time()
    resolved = False

    while not resolved:
        try:
            # Try resolving the tunnel hostname
            socket.gethostbyname(tunnel_host)
            resolved = True
            logger.info(f"✅ DNS resolved successfully for {tunnel_host}")
        except socket.gaierror:
            elapsed = round(time.time() - start_time, 1)
            if elapsed > 120:
                logger.error(f"❌ DNS resolution timed out after {elapsed}s")
                break
            logger.warning(f"🌐 Still waiting for DNS resolution of {tunnel_host} ({elapsed}s elapsed)")
            await asyncio.sleep(5)

    logger.info("💗 Heartbeat service started.")
