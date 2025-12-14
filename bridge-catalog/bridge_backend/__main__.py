"""
SR-AIbridge Backend Entrypoint v1.9.6f
Adaptive port binding with prebind monitor for Render's delayed PORT injection
"""
import asyncio
import os
import uvicorn
import logging
from bridge_backend.main import app
from bridge_backend.runtime.heartbeat import start_heartbeat

# Initialize logger
logger = logging.getLogger("bridge_backend.main")# -----------------------------------------------------------
# Auto-start Heartbeat Service
# -----------------------------------------------------------
import asyncio
from bridge_backend.runtime.heartbeat import start_heartbeat

@app.on_event("startup")
async def launch_heartbeat():
    """Start background heartbeat on backend startup."""
    asyncio.create_task(start_heartbeat())
    logger.info("💓 Heartbeat service auto-started with backend.")

# -----------------------------------------------------------
# Entrypoint
# -----------------------------------------------------------
if __name__ == "__main__":
    from bridge_backend.runtime.ports import resolve_port

    host = os.getenv("HOST", "0.0.0.0")
    port = resolve_port()  # Includes 2.5s prebind monitor
    print(f"[BOOT] Starting uvicorn on {host}:{port}")

    try:
        uvicorn.run(app, host=host, port=port)
    except KeyboardInterrupt:
        logger.info("🛑 Manual shutdown requested.")
    finally:
        logger.info("✅ Backend shutdown completed cleanly.")

# -----------------------------------------------------------
# Entrypoint with graceful shutdown notification
# -----------------------------------------------------------
if __name__ == "__main__":
    from bridge_backend.runtime.ports import resolve_port
    import httpx
    import subprocess

    host = os.getenv("HOST", "0.0.0.0")
    port = resolve_port()  # Includes 2.5s prebind monitor
    print(f"[BOOT] Starting uvicorn on {host}:{port}")

    try:
        uvicorn.run(app, host=host, port=port)
    except KeyboardInterrupt:
        logger.warning("🟥 Manual shutdown requested.")
    finally:
        # 1️⃣ Notify Netlify if online
        NETLIFY_URL = os.getenv("GENESIS_API_URL", "")
        if NETLIFY_URL:
            try:
                with httpx.Client(timeout=5) as client:
                    client.post(f"{NETLIFY_URL}/api/netlify/ping", json={
                        "status": "offline",
                        "timestamp": datetime.utcnow().isoformat(),
                        "message": "Bridge backend shutting down gracefully."
                    })
                    logger.info("📡 Notified Netlify of backend shutdown.")
            except Exception as e:
                logger.error(f"⚠️ Netlify shutdown notice failed: {e}")

        # 2️⃣ Attempt to close Cloudflare tunnel
        try:
            subprocess.run(["pkill", "-f", "cloudflared"], check=False)
            logger.info("🌩️ Cloudflare tunnel process terminated.")
        except Exception as e:
            logger.error(f"⚠️ Cloudflare shutdown failed: {e}")

        # 3️⃣ Final system message
        logger.info("✅ Backend shutdown completed cleanly.")
