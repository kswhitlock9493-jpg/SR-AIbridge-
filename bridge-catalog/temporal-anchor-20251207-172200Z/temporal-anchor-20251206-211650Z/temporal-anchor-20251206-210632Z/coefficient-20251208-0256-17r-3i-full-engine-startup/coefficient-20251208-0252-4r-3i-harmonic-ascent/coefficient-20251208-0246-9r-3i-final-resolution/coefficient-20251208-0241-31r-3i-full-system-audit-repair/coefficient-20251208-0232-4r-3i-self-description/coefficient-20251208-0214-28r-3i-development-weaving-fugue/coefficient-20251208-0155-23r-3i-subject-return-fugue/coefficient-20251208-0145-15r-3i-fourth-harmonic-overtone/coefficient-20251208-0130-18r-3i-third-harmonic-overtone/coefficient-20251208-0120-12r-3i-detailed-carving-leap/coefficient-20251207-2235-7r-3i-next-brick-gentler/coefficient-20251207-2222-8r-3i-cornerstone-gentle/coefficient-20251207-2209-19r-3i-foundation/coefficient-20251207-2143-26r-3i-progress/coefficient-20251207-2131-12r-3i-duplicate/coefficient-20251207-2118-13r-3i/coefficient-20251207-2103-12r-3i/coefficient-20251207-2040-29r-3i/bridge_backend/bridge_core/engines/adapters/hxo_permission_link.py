"""
HXO Permission Link Adapter
RBAC enforcement for HXO operations (Admiral-locked)
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


# HXO capabilities (Admiral-only by default)
HXO_CAPABILITIES = {
    "hxo:plan": {
        "description": "Create HXO plans",
        "default_roles": ["admiral"]
    },
    "hxo:submit": {
        "description": "Submit HXO plans for execution",
        "default_roles": ["admiral"]
    },
    "hxo:abort": {
        "description": "Abort running HXO plans",
        "default_roles": ["admiral"]
    },
    "hxo:priority": {
        "description": "Set plan execution priority",
        "default_roles": ["admiral"]
    },
    "hxo:certify": {
        "description": "Request Truth certification",
        "default_roles": ["admiral"]
    },
    "hxo:force-merge": {
        "description": "Force merge non-idempotent operations",
        "default_roles": ["admiral"]
    },
    "hxo:replay": {
        "description": "Replay failed plan subtrees",
        "default_roles": ["admiral"]
    },
    "hxo:view": {
        "description": "View HXO status and reports",
        "default_roles": ["admiral", "captain"]
    },
    "hxo:audit": {
        "description": "View HXO audit logs",
        "default_roles": ["admiral", "captain"]
    }
}


def check_permission(user_role: str, capability: str) -> bool:
    """
    Check if a user role has a specific HXO capability.
    
    Args:
        user_role: User role (admiral, captain, etc.)
        capability: HXO capability (e.g., "hxo:plan")
        
    Returns:
        True if user has permission
    """
    cap_info = HXO_CAPABILITIES.get(capability)
    if not cap_info:
        logger.warning(f"[HXO Permission Link] Unknown capability: {capability}")
        return False
    
    allowed_roles = cap_info.get("default_roles", [])
    return user_role.lower() in allowed_roles


async def enforce_admiral_only(user_data: Dict[str, Any], operation: str) -> bool:
    """
    Enforce admiral-only access for sensitive operations.
    
    Args:
        user_data: User data (must include 'role')
        operation: Operation being attempted
        
    Returns:
        True if user is authorized
        
    Raises:
        PermissionError if user is not authorized
    """
    user_role = user_data.get("role", "guest")
    
    if user_role.lower() != "admiral":
        logger.warning(f"[HXO Permission Link] Unauthorized {operation} attempt by {user_role}")
        raise PermissionError(f"Operation '{operation}' requires admiral role")
    
    return True


async def check_plan_permission(user_data: Dict[str, Any], plan_data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """
    Check if user has permission to submit a specific plan.
    
    Args:
        user_data: User data
        plan_data: Plan configuration
        
    Returns:
        (is_authorized, error_message)
    """
    try:
        user_role = user_data.get("role", "guest")
        
        # Check basic submit permission
        if not check_permission(user_role, "hxo:submit"):
            return False, f"Role '{user_role}' does not have hxo:submit permission"
        
        # Check for dangerous operations
        for stage in plan_data.get("stages", []):
            # Check for non-idempotent operations
            if stage.get("non_idempotent", False):
                if not check_permission(user_role, "hxo:force-merge"):
                    return False, "Non-idempotent operations require hxo:force-merge capability"
        
        return True, None
        
    except Exception as e:
        logger.error(f"[HXO Permission Link] Permission check failed: {e}")
        return False, str(e)


async def audit_operation(user_data: Dict[str, Any], operation: str, details: Dict[str, Any]):
    """
    Audit an HXO operation.
    
    Args:
        user_data: User data
        operation: Operation performed
        details: Operation details
    """
    try:
        from bridge_backend.genesis.bus import genesis_bus
        
        if not genesis_bus.is_enabled():
            logger.debug("[HXO Permission Link] Genesis bus disabled")
            return
        
        # Publish audit event
        await genesis_bus.publish("hxo.audit", {
            "user": user_data.get("username", "unknown"),
            "role": user_data.get("role", "guest"),
            "operation": operation,
            "details": details,
            "timestamp": _get_timestamp()
        })
        
        logger.info(f"[HXO Permission Link] Audited {operation} by {user_data.get('username', 'unknown')}")
        
    except ImportError:
        logger.debug("[HXO Permission Link] Genesis bus not available")
    except Exception as e:
        logger.error(f"[HXO Permission Link] Audit failed: {e}")


def _get_timestamp() -> str:
    """Get ISO timestamp"""
    from datetime import datetime, UTC
    return datetime.now(UTC).isoformat()
