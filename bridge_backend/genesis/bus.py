"""
Genesis Event Bus Multiplexer
Central event distribution for the entire Genesis organism
"""

from typing import Callable, Dict, Any, DefaultDict, List, Optional
from collections import defaultdict
import asyncio
import logging
import os
from datetime import datetime, UTC

logger = logging.getLogger(__name__)


class GenesisEventBus:
    """
    Genesis Event Multiplexer - Central nervous system for all engines
    
    Topics:
        genesis.intent - Intent propagation across engines
        genesis.fact - Fact synchronization and certification
        genesis.heal - Repair requests and confirmations
        genesis.create - Emergent build and synthesis
        genesis.echo - Introspective telemetry for the entire organism
    """
    
    def __init__(self):
        self._subs: DefaultDict[str, List[Callable]] = defaultdict(list)
        self._lock = asyncio.Lock()
        self._enabled = os.getenv("GENESIS_MODE", "enabled").lower() == "enabled"
        self._strict_policy = os.getenv("GENESIS_STRICT_POLICY", "true").lower() == "true"
        self._max_crosssignal = int(os.getenv("GENESIS_MAX_CROSSSIGNAL", "1024"))
        self._trace_level = int(os.getenv("GENESIS_TRACE_LEVEL", "2"))
        self._event_count = 0
        self._event_history: List[Dict[str, Any]] = []
        
        # Topic registry for validation
        self._valid_topics = {
            "genesis.intent",
            "genesis.fact",
            "genesis.heal",
            "genesis.create",
            "genesis.echo",
            # Legacy compatibility
            "blueprint.events",
            "deploy.signals",
            "deploy.facts",
            "deploy.actions",
            "deploy.graph",
            # Triage topics for autonomy integration
            "triage.api",
            "triage.endpoint",
            "triage.diagnostics",
            # Federation topics for autonomy integration
            "federation.events",
            "federation.heartbeat",
            # Parity topics for autonomy integration
            "parity.check",
            "parity.autofix",
            # Super Engines topics for autonomy integration
            "scrolltongue.analysis",
            "scrolltongue.translation", 
            "scrolltongue.pattern",
            "commerceforge.trade",
            "commerceforge.market",
            "commerceforge.portfolio",
            "auroraforge.visual",
            "auroraforge.creative",
            "auroraforge.render",
            "chronicleloom.chronicle",
            "chronicleloom.timeline",
            "chronicleloom.event",
            "calculuscore.computation",
            "calculuscore.optimization",
            "calculuscore.analysis",
            "qhelmsingularity.quantum",
            "qhelmsingularity.advanced",
            "qhelmsingularity.simulation",
            # Specialized engines topics
            "screen.interaction",
            "screen.render",
            "indoctrination.training",
            "indoctrination.knowledge",
            "agents_foundry.agent_created",
            "agents_foundry.agent_deployed",
            # Core systems topics
            "fleet.command",
            "fleet.status",
            "custody.state",
            "custody.transfer",
            "console.command",
            "console.output",
            "captains.policy",
            "captains.decision",
            "guardians.validation",
            "guardians.alert",
            "registry.update",
            "registry.query",
            "doctrine.compliance",
            "doctrine.violation",
            # Tools and runtime topics
            "firewall.threat",
            "firewall.analysis",
            "network.diagnostics",
            "network.status",
            "health.check",
            "health.status",
            "runtime.deploy",
            "runtime.status",
            "metrics.snapshot",
            "metrics.anomaly",
        }
        
        logger.info(f"🌌 Genesis Event Bus initialized (enabled={self._enabled}, strict={self._strict_policy})")
    
    def is_enabled(self) -> bool:
        """Check if Genesis mode is enabled"""
        return self._enabled
    
    async def publish(self, topic: str, event: Dict[str, Any]):
        """
        Publish event to Genesis bus with validation and tracing
        
        Args:
            topic: Event topic (must be valid Genesis topic)
            event: Event payload dictionary
        """
        if not self._enabled:
            logger.debug(f"Genesis bus disabled, skipping event on {topic}")
            return
        
        # Validate topic in strict mode
        if self._strict_policy and topic not in self._valid_topics:
            logger.warning(f"⚠️ Invalid Genesis topic: {topic}")
            if self._trace_level >= 1:
                logger.debug(f"Valid topics: {self._valid_topics}")
            return
        
        async with self._lock:
            # Add Genesis metadata
            enriched = {
                **event,
                "_genesis_timestamp": datetime.now(UTC).isoformat().replace('+00:00', 'Z'),
                "_genesis_topic": topic,
                "_genesis_seq": self._event_count,
            }
            
            self._event_count += 1
            
            # Store in history for introspection
            if len(self._event_history) >= self._max_crosssignal:
                self._event_history.pop(0)
            self._event_history.append({
                "topic": topic,
                "timestamp": enriched["_genesis_timestamp"],
                "seq": enriched["_genesis_seq"],
                "type": event.get("type", "unknown"),
            })
            
            # Trace logging
            if self._trace_level >= 2:
                logger.debug(f"📡 Genesis event [{topic}]: {event.get('type', 'unknown')}")
            
            # Fan out to subscribers
            subscribers = self._subs.get(topic, [])
            for sub in subscribers:
                try:
                    result = sub(enriched)
                    if asyncio.iscoroutine(result):
                        await result
                except Exception as ex:
                    logger.error(f"❌ Genesis subscriber error on {topic}: {ex}")
                    if self._trace_level >= 3:
                        logger.exception(ex)
    
    def subscribe(self, topic: str, handler: Callable[[Dict[str, Any]], Any]):
        """
        Subscribe to Genesis event topic
        
        Args:
            topic: Topic name to subscribe to
            handler: Callback function (sync or async)
        """
        if self._strict_policy and topic not in self._valid_topics:
            logger.warning(f"⚠️ Subscribing to non-standard topic: {topic}")
        
        self._subs[topic].append(handler)
        logger.info(f"📡 Genesis subscription: {topic} (total subscribers: {len(self._subs[topic])})")
    
    def get_event_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get recent event history for introspection"""
        if limit:
            return self._event_history[-limit:]
        return self._event_history.copy()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get Genesis bus statistics"""
        return {
            "enabled": self._enabled,
            "strict_policy": self._strict_policy,
            "total_events": self._event_count,
            "topics": {topic: len(subs) for topic, subs in self._subs.items()},
            "history_size": len(self._event_history),
            "max_crosssignal": self._max_crosssignal,
        }


# Global singleton Genesis bus instance
genesis_bus = GenesisEventBus()
