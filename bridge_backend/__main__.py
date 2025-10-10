"""
SR-AIbridge Backend Entrypoint
Ensures Render $PORT binding is always respected
"""
import os
import uvicorn
from bridge_backend.main import app

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host=host, port=port)
