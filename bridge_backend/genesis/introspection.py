"""
Genesis Introspection
Provides system heartbeat, snapshot, and health status reporting for orchestration.
"""

import asyncio
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class GenesisIntrospection:
    """
    The Introspection subsystem tracks system health, metrics, and status snapshots
    used by the Genesis Orchestrator.
    """

    def __init__(self):
        self._healthy_components = {}
        self._last_heartbeat = None
        self._heartbeat_interval = 5.0  # seconds
        self._running = False

    async def start(self):
        """Begin periodic heartbeat monitoring."""
        if self._running:
            return
        self._running = True
        asyncio.create_task(self._heartbeat_loop())
        logger.info("🔍 Genesis Introspection initialized")

    async def _heartbeat_loop(self):
        """Continuously update heartbeat timestamp and simulate component checks."""
        while self._running:
            self.heartbeat()
            await asyncio.sleep(self._heartbeat_interval)

    def heartbeat(self):
        """Mark the system as alive."""
        self._last_heartbeat = datetime.utcnow()
        logger.debug(f"💓 Genesis heartbeat at {self._last_heartbeat.isoformat()}")

    def snapshot(self):
        """Return a snapshot of current introspection state."""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "last_heartbeat": self._last_heartbeat.isoformat() if self._last_heartbeat else None,
            "healthy_components": self._healthy_components,
        }

    def health_status(self):
        """Return an aggregated system health report."""
        overall_healthy = all(self._healthy_components.values()) if self._healthy_components else True
        return {
            "overall_healthy": overall_healthy,
            "components": self._healthy_components,
        }

    def update_component(self, name: str, healthy: bool):
        """Mark an individual component as healthy/unhealthy."""
        self._healthy_components[name] = healthy
        state = "✅ healthy" if healthy else "❌ unhealthy"
        logger.info(f"📊 Component '{name}' marked as {state}")

    async def stop(self):
        """Stop introspection loop."""
        self._running = False
        logger.info("🧩 Genesis Introspection stopped")


# Global singleton instance
genesis_introspection = GenesisIntrospection()
