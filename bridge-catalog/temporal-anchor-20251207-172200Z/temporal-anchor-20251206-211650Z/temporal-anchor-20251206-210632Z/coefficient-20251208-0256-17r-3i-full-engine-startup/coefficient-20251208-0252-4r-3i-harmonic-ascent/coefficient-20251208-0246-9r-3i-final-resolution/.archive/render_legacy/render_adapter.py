"""
Render adapter for Env Steward
"""

import os
import logging

logger = logging.getLogger(__name__)


class RenderAdapter:
    """Adapter for Render.com environment variables"""
    
    name = "render"
    
    def enabled(self) -> bool:
        """Check if Render adapter is enabled"""
        return os.getenv("STEWARD_RENDER_ENABLED", "false").lower() == "true"
    
    async def apply(self, changes):
        """
        Apply environment variable changes to Render
        
        Args:
            changes: List of changes to apply
            
        Returns:
            Result dictionary
        """
        token = os.getenv("RENDER_API_TOKEN", "")
        service_id = os.getenv("RENDER_SERVICE_ID", "")
        
        if not token or not service_id:
            logger.warning("Render adapter: missing token or service_id")
            return {
                "ok": False,
                "reason": "Render write disabled or token/service missing",
                "provider": self.name
            }
        
        # In production, this would call the Render API
        # For now, return success simulation
        logger.info(f"Render adapter: would apply {len(changes)} changes to service {service_id}")
        
        return {
            "ok": True,
            "updated": len(changes),
            "provider": self.name
        }
