"""
SR-AIbridge v1.9.7a — TDE-X Hypersharded Deploy Runner
Programmatic uvicorn runner with TDE-X orchestration
"""
import os
import sys
import asyncio
import uvicorn


async def _boot():
    """Boot TDE-X orchestrator without blocking server"""
    from bridge_backend.runtime.tde_x.orchestrator import run_tde_x
    asyncio.create_task(run_tde_x())


def main():
    """Main entry point for uvicorn with TDE-X integration"""
    app_path = os.environ.get("APP_IMPORT", "bridge_backend.main:app")
    
    # Render injects PORT; default 8000 for local
    port = int(os.getenv("PORT", "8000"))
    host = os.environ.get("HOST", "0.0.0.0")
    log_level = os.environ.get("LOG_LEVEL", "info").lower()
    
    # Set BRIDGE_PORT for internal logic
    os.environ["BRIDGE_PORT"] = str(port)
    
    print(f"[BOOT] 🚀 Starting SR-AIbridge v1.9.7a with TDE-X")
    print(f"[BOOT] 🌊 Host: {host}:{port}")
    print(f"[BOOT] ⚡ TDE-X will orchestrate shards in background")
    
    # Prime orchestrator
    asyncio.get_event_loop().run_until_complete(_boot())
    
    # Start uvicorn server
    uvicorn.run(app_path, host=host, port=port, log_level=log_level)


if __name__ == "__main__":
    main()
