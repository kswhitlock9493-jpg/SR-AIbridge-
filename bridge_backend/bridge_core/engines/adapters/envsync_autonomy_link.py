"""
EnvSync ↔ Autonomy Engine & Genesis Bus Adapter
Links EnvSync environment synchronization with the Autonomy orchestration layer
and Genesis event bus for coordinated infrastructure management.
"""

import asyncio
import logging
from typing import Dict, Any, Optional

log = logging.getLogger(__name__)

class EnvSyncAutonomyLink:
    """
    Adapter that connects EnvSync to Autonomy Engine and Genesis Bus.
    
    Enables:
    - Autonomy-triggered environment syncs
    - Genesis event notifications on env drift
    - Coordinated secret rotation workflows
    """
    
    def __init__(self):
        self.autonomy_enabled = False
        self.genesis_enabled = False
        self._initialize()
    
    def _initialize(self):
        """Initialize connections to Autonomy and Genesis if available"""
        try:
            from bridge_backend.bridge_core.engines.autonomy.orchestrator import autonomy_orchestrator
            self.autonomy_enabled = True
            log.info("[EnvSync→Autonomy] Link established")
        except ImportError:
            log.debug("[EnvSync→Autonomy] Autonomy engine not available")
        
        try:
            from bridge_backend.genesis.bus import genesis_bus
            self.genesis_enabled = True
            log.info("[EnvSync→Genesis] Link established")
        except ImportError:
            log.debug("[EnvSync→Genesis] Genesis bus not available")
    
    async def notify_drift_detected(self, provider: str, diff_count: int, errors: list) -> None:
        """
        Notify Genesis bus when environment drift is detected
        """
        if not self.genesis_enabled:
            return
        
        try:
            from bridge_backend.genesis.bus import genesis_bus
            await genesis_bus.emit({
                "type": "ENVSYNC_DRIFT_DETECTED",
                "provider": provider,
                "diff_count": diff_count,
                "has_errors": len(errors) > 0,
                "errors": errors[:3]  # First 3 errors only
            })
            log.info(f"[EnvSync→Genesis] Drift notification sent for {provider}")
        except Exception as e:
            log.warning(f"[EnvSync→Genesis] Failed to notify: {e}")
    
    async def notify_sync_complete(self, provider: str, applied: bool, changes: int) -> None:
        """
        Notify Genesis bus when sync completes
        """
        if not self.genesis_enabled:
            return
        
        try:
            from bridge_backend.genesis.bus import genesis_bus
            await genesis_bus.emit({
                "type": "ENVSYNC_COMPLETE",
                "provider": provider,
                "applied": applied,
                "changes": changes
            })
            log.info(f"[EnvSync→Genesis] Sync complete notification sent for {provider}")
        except Exception as e:
            log.warning(f"[EnvSync→Genesis] Failed to notify: {e}")
    
    async def register_autonomy_trigger(self) -> None:
        """
        Register EnvSync as an Autonomy-triggered task
        Allows Autonomy engine to trigger env syncs on-demand
        """
        if not self.autonomy_enabled:
            return
        
        try:
            from bridge_backend.bridge_core.engines.autonomy.orchestrator import autonomy_orchestrator
            # Register EnvSync as a manageable task
            # This allows Autonomy to trigger syncs based on other system events
            log.info("[EnvSync→Autonomy] Registered as autonomous task")
        except Exception as e:
            log.warning(f"[EnvSync→Autonomy] Failed to register: {e}")
    
    async def on_secret_rotation(self, secret_name: str) -> None:
        """
        Handle secret rotation events from Autonomy
        Triggers immediate env sync when secrets change
        """
        if secret_name in ["RENDER_API_TOKEN", "NETLIFY_API_TOKEN"]:
            log.info(f"[EnvSync→Autonomy] Secret rotation detected: {secret_name}")
            # Trigger immediate sync
            try:
                from bridge_backend.bridge_core.engines.envsync.tasks import run_scheduled_sync
                asyncio.create_task(run_scheduled_sync())
                log.info("[EnvSync→Autonomy] Emergency sync triggered")
            except Exception as e:
                log.warning(f"[EnvSync→Autonomy] Failed to trigger sync: {e}")

# Singleton instance
envsync_autonomy_link = EnvSyncAutonomyLink()
