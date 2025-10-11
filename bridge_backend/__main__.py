"""
SR-AIbridge Backend Entrypoint v1.9.6f
Adaptive port binding with prebind monitor for Render's delayed PORT injection
"""
import os
import uvicorn
from bridge_backend.main import app

if __name__ == "__main__":
    # Use adaptive port resolution from runtime.ports
    from bridge_backend.runtime.ports import resolve_port
    host = os.getenv("HOST", "0.0.0.0")
    port = resolve_port()  # Includes 2.5s prebind monitor
    
    print(f"[BOOT] Starting uvicorn on {host}:{port}")
    uvicorn.run(app, host=host, port=port)
