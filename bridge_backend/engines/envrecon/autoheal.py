"""
Auto-Healing Subsystem
Communicates with Genesis core via genesis.heal.env topic to auto-correct environment drift
"""

import os
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class AutoHealEngine:
    """
    Auto-healing subsystem for environment drift correction.
    Integrates with Genesis event bus to trigger healing actions.
    """
    
    def __init__(self):
        self.max_depth = int(os.getenv("GENESIS_ECHO_DEPTH_LIMIT", "10"))
        self.enabled = os.getenv("GENESIS_AUTOHEAL_ENABLED", "true").lower() == "true"
        self.current_depth = 0
    
    async def heal_environment(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """
        Attempt to heal environment based on reconciliation report.
        
        Args:
            report: EnvRecon report with drift information
            
        Returns:
            Healing summary
        """
        if not self.enabled:
            logger.info("⚠️ Auto-heal disabled")
            return {"enabled": False, "healed": []}
        
        if self.current_depth >= self.max_depth:
            logger.warning(f"⚠️ Auto-heal depth limit reached ({self.max_depth})")
            return {"enabled": True, "healed": [], "depth_limit_reached": True}
        
        self.current_depth += 1
        healed = []
        
        try:
            # Attempt to emit heal event to Genesis
            await self._emit_heal_event(report)
            
            # Track what was auto-fixed
            missing_render = report.get("missing_in_render", [])
            missing_netlify = report.get("missing_in_netlify", [])
            
            # In a real implementation, this would trigger actual healing
            # For now, we log the intent
            for var in missing_render[:5]:  # Limit to prevent overwhelming the system
                logger.info(f"🩹 Would heal Render: {var}")
                healed.append(var)
            
            for var in missing_netlify[:5]:
                logger.info(f"🩹 Would heal Netlify: {var}")
                healed.append(var)
            
            return {
                "enabled": True,
                "healed": healed,
                "depth": self.current_depth
            }
        
        except Exception as e:
            logger.error(f"❌ Auto-heal failed: {e}")
            return {"enabled": True, "healed": [], "error": str(e)}
        
        finally:
            self.current_depth -= 1
    
    async def _emit_heal_event(self, report: Dict[str, Any]):
        """Emit heal event to Genesis event bus"""
        try:
            # Try to import Genesis adapters
            from bridge_backend.genesis.adapters import emit_heal
            
            await emit_heal(
                topic="genesis.heal.env",
                source="envrecon.autoheal",
                payload={
                    "report_summary": {
                        "missing_render": len(report.get("missing_in_render", [])),
                        "missing_netlify": len(report.get("missing_in_netlify", [])),
                        "conflicts": len(report.get("conflicts", {}))
                    },
                    "timestamp": report.get("timestamp"),
                    "autoheal_depth": self.current_depth
                }
            )
            logger.info("✅ Heal event emitted to Genesis bus")
        except ImportError:
            logger.debug("Genesis adapters not available, skipping event emission")
        except Exception as e:
            logger.warning(f"⚠️ Failed to emit heal event: {e}")
    
    def reset_depth(self):
        """Reset healing depth counter"""
        self.current_depth = 0


# Singleton instance
autoheal = AutoHealEngine()
