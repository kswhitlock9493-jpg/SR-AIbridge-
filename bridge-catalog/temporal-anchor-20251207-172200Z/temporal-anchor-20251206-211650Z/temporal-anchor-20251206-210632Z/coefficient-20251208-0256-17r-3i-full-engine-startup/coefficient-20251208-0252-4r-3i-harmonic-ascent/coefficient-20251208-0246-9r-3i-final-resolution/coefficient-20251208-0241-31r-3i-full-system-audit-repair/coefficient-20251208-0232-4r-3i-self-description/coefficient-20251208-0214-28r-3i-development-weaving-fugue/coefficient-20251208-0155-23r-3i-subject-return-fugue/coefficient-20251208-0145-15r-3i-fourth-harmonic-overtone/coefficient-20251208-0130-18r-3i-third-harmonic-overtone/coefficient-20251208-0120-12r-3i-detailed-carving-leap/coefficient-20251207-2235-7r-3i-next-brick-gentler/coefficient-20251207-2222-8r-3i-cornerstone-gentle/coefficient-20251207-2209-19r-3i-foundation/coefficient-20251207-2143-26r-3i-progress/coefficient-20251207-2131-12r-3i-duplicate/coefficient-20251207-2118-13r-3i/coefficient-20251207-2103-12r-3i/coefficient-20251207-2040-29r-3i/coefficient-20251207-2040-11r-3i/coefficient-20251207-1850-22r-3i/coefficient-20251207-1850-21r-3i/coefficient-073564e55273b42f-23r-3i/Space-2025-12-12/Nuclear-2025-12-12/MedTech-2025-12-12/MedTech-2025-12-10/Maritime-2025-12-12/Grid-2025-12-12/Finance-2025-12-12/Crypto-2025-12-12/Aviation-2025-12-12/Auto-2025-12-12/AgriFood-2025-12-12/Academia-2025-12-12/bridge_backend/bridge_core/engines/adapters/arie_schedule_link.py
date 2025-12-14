"""
ARIE Schedule Link - Genesis Timer Integration
Connects ARIE scheduler to Genesis Event Bus
"""

import os
import logging
from typing import Dict, Any
from datetime import datetime, UTC

logger = logging.getLogger(__name__)


class ARIEScheduleLink:
    """
    Links ARIE scheduler to Genesis Event Bus
    
    Subscribes to:
    - Manual trigger events (if exposed)
    
    Publishes:
    - arie.schedule.tick → timed trigger events
    - arie.schedule.summary → summary of each scheduled run
    """
    
    def __init__(self, bus=None, scheduler=None):
        self.bus = bus
        self.scheduler = scheduler
        self.enabled = os.getenv("ARIE_SCHEDULE_ENABLED", "false").lower() == "true"
        
        if self.enabled and self.bus:
            self._register_subscriptions()
    
    def _register_subscriptions(self):
        """Register Genesis event subscriptions"""
        if not self.bus:
            return
        
        # Could subscribe to manual trigger events here if needed
        # For now, manual triggers go through the scheduler API directly
        
        logger.info("[ARIE Schedule Link] Registered subscriptions")
    
    async def on_manual_trigger(self, event: Dict[str, Any]):
        """Handle manual trigger request"""
        if not self.enabled or not self.scheduler:
            return
        
        requester = event.get("requester", "unknown")
        
        try:
            result = await self.scheduler.trigger_manual_run(requester)
            
            # Publish success event
            if self.bus:
                await self.bus.publish("arie.schedule.manual", {
                    "timestamp": datetime.now(UTC).isoformat() + "Z",
                    "requester": requester,
                    "run_id": result["run_id"],
                    "success": True
                })
                
        except PermissionError as e:
            logger.warning(f"[ARIE Schedule Link] Permission denied: {e}")
            if self.bus:
                await self.bus.publish("arie.alert", {
                    "type": "permission_denied",
                    "message": str(e),
                    "timestamp": datetime.now(UTC).isoformat() + "Z",
                    "severity": "medium"
                })
        except Exception as e:
            logger.exception(f"[ARIE Schedule Link] Manual trigger failed: {e}")
            if self.bus:
                await self.bus.publish("arie.alert", {
                    "type": "manual_trigger_failed",
                    "message": str(e),
                    "timestamp": datetime.now(UTC).isoformat() + "Z",
                    "severity": "high"
                })
