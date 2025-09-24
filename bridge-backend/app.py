"""
FastAPI backend entry point for SR-AIbridge
Simple wrapper around main.py for compatibility with deployment requirements.
"""
from main import app

# Export the FastAPI app instance for deployment
__all__ = ["app"]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)