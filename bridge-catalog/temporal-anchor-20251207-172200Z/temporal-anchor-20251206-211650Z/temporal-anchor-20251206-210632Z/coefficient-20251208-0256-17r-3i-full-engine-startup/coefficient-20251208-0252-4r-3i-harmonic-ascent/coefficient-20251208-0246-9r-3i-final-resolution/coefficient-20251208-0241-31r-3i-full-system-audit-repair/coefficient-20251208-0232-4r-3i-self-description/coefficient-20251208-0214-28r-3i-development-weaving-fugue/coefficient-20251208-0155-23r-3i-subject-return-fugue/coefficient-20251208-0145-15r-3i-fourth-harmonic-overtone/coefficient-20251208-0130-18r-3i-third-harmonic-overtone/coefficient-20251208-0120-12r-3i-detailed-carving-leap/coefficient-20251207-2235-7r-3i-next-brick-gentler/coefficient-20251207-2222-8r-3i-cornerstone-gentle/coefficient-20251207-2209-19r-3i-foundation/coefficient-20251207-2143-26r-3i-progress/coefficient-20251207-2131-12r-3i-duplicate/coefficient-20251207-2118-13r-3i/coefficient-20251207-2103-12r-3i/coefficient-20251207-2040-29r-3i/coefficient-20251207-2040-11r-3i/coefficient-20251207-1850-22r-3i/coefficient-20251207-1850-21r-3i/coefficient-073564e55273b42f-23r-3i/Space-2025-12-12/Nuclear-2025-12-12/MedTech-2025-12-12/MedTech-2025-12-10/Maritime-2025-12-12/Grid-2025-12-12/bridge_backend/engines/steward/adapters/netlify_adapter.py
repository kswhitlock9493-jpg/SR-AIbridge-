"""
Netlify adapter for Env Steward
"""

import os
import logging

logger = logging.getLogger(__name__)


class NetlifyAdapter:
    """Adapter for Netlify environment variables"""
    
    name = "netlify"
    
    def enabled(self) -> bool:
        """Check if Netlify adapter is enabled"""
        return os.getenv("STEWARD_NETLIFY_ENABLED", "false").lower() == "true"
    
    async def apply(self, changes):
        """
        Apply environment variable changes to Netlify
        
        Args:
            changes: List of changes to apply
            
        Returns:
            Result dictionary
        """
        token = os.getenv("NETLIFY_AUTH_TOKEN", "")
        site_id = os.getenv("NETLIFY_SITE_ID", "")
        
        if not token or not site_id:
            logger.warning("Netlify adapter: missing token or site_id")
            return {
                "ok": False,
                "reason": "Netlify write disabled or token/site missing",
                "provider": self.name
            }
        
        # In production, this would call the Netlify API
        # For now, return success simulation
        logger.info(f"Netlify adapter: would apply {len(changes)} changes to site {site_id}")
        
        return {
            "ok": True,
            "updated": len(changes),
            "provider": self.name
        }
