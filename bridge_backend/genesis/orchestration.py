"""
Genesis Orchestration Loop
Core coordination loop for the Genesis organism
Coordinates cross-engine signals and manages system health and introspection
"""

from typing import Dict, Any, Optional
import asyncio
import logging
import os

logger = logging.getLogger(__name__)


class GenesisOrchestrator:
    """Core orchestration loop for Genesis."""

    def __init__(self):
        self._running = False
        self._loop_task: Optional[asyncio.Task] = None
        self._enabled = os.getenv("GENESIS_MODE", "enabled").lower() == "enabled"
        self._heartbeat_interval = int(os.getenv("HEARTBEAT_INTERVAL", 5))

        logger.info("🧠 Genesis Orchestrator initialized")

    async def start(self):
        """Start the Genesis orchestration loop."""
        if not self._enabled:
            logger.info("Genesis orchestration disabled via GENESIS_MODE")
            return

        if self._running:
            logger.warning("⚠️ Genesis orchestration already running")
            return

        self._running = True
        self._loop_task = asyncio.create_task(self._orchestration_loop())
        logger.info("✅ Genesis orchestration loop started")

    async def stop(self):
        """Stop the Genesis orchestration loop."""
        self._running = False
        if self._loop_task:
            self._loop_task.cancel()
        logger.info("🛑 Genesis orchestration loop stopped")

    async def _orchestration_loop(self):
        """Main orchestration loop"""
        from .bus import genesis_bus
        from .manifest import genesis_manifest
        from .introspection import genesis_introspection

        logger.info("🌐 Genesis orchestration loop engaged")

        # Initialize manifest
        genesis_manifest.sync_from_blueprint_registry()

        while self._running:
            try:
                # Heartbeat pulse
                genesis_introspection.heartbeat()

                # Publish echo event for system introspection
                if hasattr(genesis_introspection, "snapshot"):
                    echo_report = genesis_introspection.snapshot()
                elif hasattr(genesis_introspection, "status"):
                    echo_report = genesis_introspection.status()
                elif hasattr(genesis_introspection, "capture"):
                    echo_report = genesis_introspection.capture()
                else:
                    echo_report = {"status": "unknown", "source": "introspection"}

                logger.debug(f"🧠 Introspection snapshot prepared: {list(echo_report.keys())}")

                # Prevent echo recursion (ignore our own orchestration-originated events)
                if echo_report.get("source") == "orchestration":
                    logger.debug("🌀 Skipped self-originating echo to prevent recursion loop")
                    continue

                echo_report["source"] = "orchestration"
                await genesis_bus.publish("genesis.echo", echo_report)

                # Check system health
                health = genesis_introspection.health_status()
                if not health.get("overall_healthy", True):
                    logger.warning(f"⚠️ System health degraded: {health}")

                    # Publish heal event for degraded components
                    for component, is_healthy in health.get("components", {}).items():
                        if not is_healthy:
                            await genesis_bus.publish("genesis.heal", {
                                "type": "heal.request",
                                "component": component,
                                "reason": "auto-recovery"
                            })

                # Sleep for heartbeat interval
                await asyncio.sleep(self._heartbeat_interval)

            except asyncio.CancelledError:
                # Graceful shutdown
                logger.info("🛑 Genesis orchestration loop cancelled gracefully")
                break
            except Exception as e:
                logger.error(f"❌ Error in Genesis orchestration loop: {e}")
                await asyncio.sleep(self._heartbeat_interval)

    def get_status(self) -> Dict[str, Any]:
        """Get orchestrator status."""
        return {
            "running": self._running,
            "enabled": self._enabled,
            "heartbeat_interval": self._heartbeat_interval,
        }

    async def execute_action(self, action: str, params: Dict[str, Any]):
        """Execute a coordinated action across engines."""
        from .bus import genesis_bus

        logger.info(f"🚀 Executing Genesis action: {action}")
        await genesis_bus.publish("genesis.intent", {
            "type": "intent.action",
            "action": action,
            "params": params,
        })

        # TODO: Implement actual action execution
        return {
            "action": action,
            "status": "acknowledged",
            "params": params,
        }


# Global singleton orchestrator instance
genesis_orchestrator = GenesisOrchestrator()
