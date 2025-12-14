"""
Genesis Orchestration Loop
Core coordination loop for the Genesis organism
"""

from typing import Dict, Any, Optional
import asyncio
import logging
import os

logger = logging.getLogger(__name__)


class GenesisOrchestrator:
    """
    Core orchestration loop for Genesis.
    Coordinates cross-engine signals, manages self-healing, and enforces guardrails.
    """
    
    def __init__(self):
        self._running = False
        self._loop_task: Optional[asyncio.Task] = None
        self._enabled = os.getenv("GENESIS_MODE", "enabled").lower() == "enabled"
        self._heartbeat_interval = int(os.getenv("GENESIS_HEARTBEAT_INTERVAL", "15"))
        
        logger.info("🎭 Genesis Orchestrator initialized")
    
    async def start(self):
        """Start the Genesis orchestration loop"""
        if not self._enabled:
            logger.info("Genesis orchestration disabled (GENESIS_MODE not enabled)")
            return
        
        if self._running:
            logger.warning("Genesis orchestrator already running")
            return
        
        self._running = True
        self._loop_task = asyncio.create_task(self._orchestration_loop())
        logger.info("✅ Genesis orchestration loop started")
    
    async def stop(self):
        """Stop the Genesis orchestration loop"""
        if not self._running:
            return
        
        self._running = False
        if self._loop_task:
            self._loop_task.cancel()
            try:
                await self._loop_task
            except asyncio.CancelledError:
                pass
        
        logger.info("⏸️ Genesis orchestration loop stopped")
    
    async def _orchestration_loop(self):
        """Main orchestration loop"""
        from .bus import genesis_bus
        from .manifest import genesis_manifest
        from .introspection import genesis_introspection
        
        logger.info("🌀 Genesis orchestration loop active")
        
        # Initialize manifest
        genesis_manifest.sync_from_blueprint_registry()
        
        while self._running:
            try:
                # Heartbeat pulse
                genesis_introspection.heartbeat()
                
                # Publish echo event for system introspection
                echo_report = genesis_introspection.generate_echo_report()
                await genesis_bus.publish("genesis.echo", echo_report)
                
                # Check system health
                health = genesis_introspection.get_health_status()
                if not health["overall_healthy"]:
                    logger.warning(f"⚠️ System health degraded: {health['healthy_count']}/{health['total_count']} healthy")
                    
                    # Publish heal event for degraded components
                    for component, is_healthy in health["components"].items():
                        if not is_healthy:
                            await genesis_bus.publish("genesis.heal", {
                                "type": "heal.request",
                                "component": component,
                                "reason": "health_check_failed",
                            })
                
                # Sleep for heartbeat interval
                await asyncio.sleep(self._heartbeat_interval)
                
            except asyncio.CancelledError:
                raise
            except Exception as e:
                logger.error(f"❌ Error in Genesis orchestration loop: {e}")
                await asyncio.sleep(self._heartbeat_interval)
    
    def get_status(self) -> Dict[str, Any]:
        """Get orchestrator status"""
        return {
            "running": self._running,
            "enabled": self._enabled,
            "heartbeat_interval": self._heartbeat_interval,
        }
    
    async def execute_action(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a coordinated action across engines with guardrails
        
        Args:
            action: Action to execute
            params: Action parameters
            
        Returns:
            Execution result
        """
        from .bus import genesis_bus
        
        logger.info(f"Executing Genesis action: {action}")
        
        # Publish intent event
        await genesis_bus.publish("genesis.intent", {
            "type": "intent.action",
            "action": action,
            "params": params,
        })
        
        # TODO: Implement actual action execution with guardrails from Blueprint/Guardians
        # For now, just acknowledge
        return {
            "action": action,
            "status": "acknowledged",
            "params": params,
        }


# Global singleton orchestrator instance
genesis_orchestrator = GenesisOrchestrator()
