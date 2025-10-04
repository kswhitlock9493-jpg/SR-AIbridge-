from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

# Import CascadeEngine for tier management
try:
    from bridge_core.engines.cascade.service import CascadeEngine
except ImportError:
    from bridge_backend.bridge_core.engines.cascade.service import CascadeEngine

# Simple RBAC matrix
ROLE_MATRIX = {
    "admiral": {"all": True},  # you
    "captain": {"admin": False, "agents": True, "vault": True, "screen": False, "view_own_missions": True, "view_agent_jobs": False},
    "agent": {"self": True, "vault": False, "view_own_missions": False, "execute_jobs": True},
}

class PermissionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # For now, allow unauthenticated requests to pass through
        # In production, this would be stricter with proper authentication
        user = getattr(request.state, "user", None)
        
        # If no user, check if this is a protected endpoint
        if not user:
            # Get user_id from query params as a fallback (mock auth pattern)
            user_id = request.query_params.get("user_id", "test_captain")
            
            # Create a mock user object for now
            class MockUser:
                def __init__(self, uid):
                    self.id = uid
                    self.role = "captain"  # default role
                    self.project = None
            
            user = MockUser(user_id)
            request.state.user = user

        # Cascade decides effective tier
        cascade_state = CascadeEngine().get_state(user.id)
        tier = cascade_state.get("tier", "free")
        role = getattr(user, "role", "captain")

        # Global tier gate
        if tier == "free" and request.url.path.startswith("/engines/leviathan"):
            return JSONResponse(
                status_code=403,
                content={"detail": "leviathan_locked_free"}
            )

        if tier == "free" and request.url.path.startswith("/engines/agents"):
            return JSONResponse(
                status_code=403,
                content={"detail": "agents_locked_free"}
            )

        # Role-based gate
        perms = ROLE_MATRIX.get(role, {})
        if not perms.get("all", False):
            if "admin" in request.url.path and not perms.get("admin", False):
                return JSONResponse(
                    status_code=403,
                    content={"detail": "role_restricted"}
                )

        # Project-specific gate (if autonomy task has restrictions)
        if hasattr(user, "project") and user.project and request.url.path.startswith("/vault/"):
            if user.project not in request.url.path:
                return JSONResponse(
                    status_code=403,
                    content={"detail": "project_scope_violation"}
                )

        response = await call_next(request)
        return response
