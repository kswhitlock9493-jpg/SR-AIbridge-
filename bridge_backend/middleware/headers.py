"""
Netlify ↔ Render Header Synchronization Middleware for v1.9.6b

Ensures consistent headers across deployment environments.
Standardizes CORS, Cache-Control, and custom Bridge headers.
"""
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import os

logger = logging.getLogger(__name__)

class HeaderSyncMiddleware(BaseHTTPMiddleware):
    """
    Middleware to synchronize headers between Netlify and Render deployments.
    Ensures consistent behavior across all environments.
    """
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Add standard Bridge headers
        response.headers["X-Bridge-Node"] = os.getenv("BRIDGE_NODE", "render-primary")
        response.headers["X-Bridge-Version"] = os.getenv("APP_VERSION", "v1.9.6b")
        
        # Standardize Cache-Control for API responses
        if request.url.path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        
        # Add CORS headers if not already set by CORSMiddleware
        # This ensures consistency even if CORSMiddleware is bypassed
        if "access-control-allow-origin" not in [h.lower() for h in response.headers.keys()]:
            origin = request.headers.get("origin")
            allowed_origins = os.getenv(
                "ALLOWED_ORIGINS",
                "https://sr-aibridge.netlify.app,https://sr-aibridge.onrender.com"
            ).split(",")
            
            if origin in allowed_origins or os.getenv("CORS_ALLOW_ALL", "false").lower() == "true":
                response.headers["Access-Control-Allow-Origin"] = origin or "*"
                response.headers["Access-Control-Allow-Credentials"] = "true"
        
        return response
