"""
ARIE Permission Link - RBAC gates for ARIE operations
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class ARIEPermissionLink:
    """
    RBAC gates for ARIE operations
    
    Capabilities:
    - arie:scan - Can run scans (captain+)
    - arie:fix - Can apply fixes (admiral only)
    - arie:rollback - Can rollback patches (admiral only)
    - arie:configure - Can change configuration (admiral only)
    """
    
    # Default role mappings
    DEFAULT_POLICY = {
        "arie:scan": ["captain", "admiral"],
        "arie:fix": ["admiral"],
        "arie:rollback": ["admiral"],
        "arie:configure": ["admiral"]
    }
    
    def __init__(self, permission_engine=None):
        self.permission_engine = permission_engine
        self.policy = self.DEFAULT_POLICY.copy()
    
    async def check_capability(self, user_role: str, capability: str) -> bool:
        """
        Check if user role has capability
        
        Args:
            user_role: User's role (e.g., "admiral", "captain")
            capability: Capability to check (e.g., "arie:scan")
        
        Returns:
            True if user has capability, False otherwise
        """
        if self.permission_engine:
            # Use actual Permission Engine
            try:
                return await self.permission_engine.check(user_role, capability)
            except Exception as e:
                logger.exception(f"[ARIE Permission] Error checking permission: {e}")
                return False
        
        # Fallback to default policy
        allowed_roles = self.policy.get(capability, [])
        return user_role in allowed_roles
    
    def update_policy(self, capability: str, roles: list):
        """Update policy for a capability"""
        self.policy[capability] = roles
        logger.info(f"[ARIE Permission] Updated policy for {capability}: {roles}")
    
    def get_policy(self) -> dict:
        """Get current policy"""
        return self.policy.copy()
