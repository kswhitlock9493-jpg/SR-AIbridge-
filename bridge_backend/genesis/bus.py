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
            # Umbra Cognitive Stack topics (v1.9.7d)
            "umbra.anomaly.detected",
            "umbra.pipeline.repaired",
            "umbra.echo.recorded",
            "umbra.memory.learned",
            # Umbra Lattice Memory topics (v1.9.7g)
            "umbra.lattice.recorded",
            "umbra.lattice.certified",
            "umbra.lattice.cert_failed",
            "umbra.lattice.snapshot",
            "umbra.lattice.bloom",
            "truth.certify.cognitive",
            "hxo.echo.sync",
            "doctrine.violation",
            # HXO Nexus topics for connectivity
            "hxo.nexus.initialized",
            "hxo.nexus.command",
            "hxo.nexus.query",
            "hxo.coordination.started",
            "hxo.coordination.complete",
            "hxo.link.autonomy",
            "hxo.link.blueprint",
            "hxo.link.truth",
            "hxo.link.cascade",
            "hxo.link.federation",
            "hxo.link.parser",
            "hxo.link.leviathan",
            "hxo.link.arie",
            "hxo.link.envrecon",
            "hxo.telemetry.metrics",
            "hxo.heal.trigger",
            "hxo.heal.complete",
            "hxo.status.summary",
            # Chimera Deployment Engine topics (v1.9.7c)
            "deploy.initiated",
            "deploy.heal.intent",
            "deploy.heal.complete",
            "deploy.certified",
            "chimera.simulate.start",
            "chimera.simulate.complete",
            "chimera.deploy.start",
            "chimera.deploy.complete",
            "chimera.certify.start",
            "chimera.certify.complete",
            "chimera.rollback.triggered",
            # Chimera Preflight topics (v1.9.6r)
            "chimera.preflight.start",
            "chimera.preflight.ok",
            "chimera.preflight.fail",
            "chimera.deploy.heal.intent",
            "chimera.deploy.heal.applied",
            "chimera.deploy.heal.rollback",
            "deploy.preview.requested",
            "deploy.preview.failed",
            "deploy.preview.requeued",
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
            # Heritage and MAS topics
            "mas.agent",
            "mas.coordination",
            "mas.task",
            "mas.failure",
            "heritage.agent",
            "heritage.bridge",
            "heal.events",
            # Deployment platform topics for autonomy integration
            "deploy.netlify",
            "deploy.render",
            "deploy.github",
            "deploy.platform.start",
            "deploy.platform.success",
            "deploy.platform.failure",
            # EnvSync topics for environment synchronization
            "deploy.platform.sync",
            "envsync.drift",
            "envsync.sync",
            "envsync.complete",
            # EnvRecon topics for cross-platform reconciliation
            "envrecon.drift",
            "envrecon.audit",
            "envrecon.heal",
            "envrecon.sync",
            # EnvMirror topics for GitHub ↔ Render ↔ Netlify sync (v1.9.6x)
            "envmirror.sync.start",
            "envmirror.sync.complete",
            "envmirror.audit",
            # EnvDuo topics for ARIE + EnvRecon hybrid audit (v1.9.6x)
            "envduo.audit",
            "envduo.heal",
            # Steward topics for admiral-tier environment orchestration
            "steward.intent",
            "steward.plan",
            "steward.apply",
            "steward.result",
            "steward.rollback",
            "steward.cap.issued",
            # ARIE topics for autonomous repository integrity
            "arie.audit",
            "arie.fix.intent",
            "arie.fix.applied",
            "arie.fix.rollback",
            "arie.alert",
            "arie.schedule.tick",
            "arie.schedule.summary",
            "arie.schedule.manual",
            # HXO topics for Hypshard-X Orchestrator
            "hxo.plan",
            "hxo.shard.created",
            "hxo.shard.claimed",
            "hxo.shard.done",
            "hxo.shard.failed",
            "hxo.aggregate.ready",
            "hxo.aggregate.certify",
            "hxo.aggregate.finalized",
            "hxo.aggregate.failed",
            "hxo.autotune.signal",
            "hxo.alert",
            "hxo.audit",
            # TDE orchestrator topics (v1.9.6q)
            "deploy.tde.orchestrator.completed",
            "deploy.tde.orchestrator.failed",
            # Autonomy tuning signal (v1.9.6q)
            "autonomy.tuning.signal",
            # Autonomy Decision Layer topics (v1.9.6s)
            "autonomy.heal.applied",
            "autonomy.heal.error",
            "autonomy.circuit.open",
            "autonomy.circuit.closed",
            "deploy.netlify.preview_failed",
            "arie.deprecated.detected",
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
            
            # Apply Guardians gate check
            try:
                from bridge_backend.bridge_core.guardians.gate import guardians_gate
                allowed, reason = guardians_gate.allow(enriched)
                if not allowed:
                    logger.warning(f"🛡️ Guardians blocked event on {topic}: {reason}")
                    # Emit audit event for blocked action
                    await self._emit_blocked_event(topic, enriched, reason)
                    return
            except Exception as e:
                logger.error(f"❌ Guardians check failed (allowing event): {e}")
            
            # Check for duplicate via persistence
            dedupe_key = event.get("dedupe_key")
            if dedupe_key:
                try:
                    from bridge_backend.genesis.persistence import genesis_persistence
                    if await genesis_persistence.is_duplicate(dedupe_key):
                        logger.debug(f"⏭️ Skipping duplicate event: {dedupe_key}")
                        return
                except Exception as e:
                    logger.error(f"❌ Dedupe check failed (allowing event): {e}")
            
            self._event_count += 1
            
            # Persist event
            try:
                from bridge_backend.genesis.persistence import genesis_persistence
                await genesis_persistence.record_event(
                    event_id=enriched.get("id", f"event-{self._event_count}"),
                    topic=topic,
                    source=enriched.get("source", "unknown"),
                    kind=enriched.get("kind", "unknown"),
                    payload=enriched.get("payload", {}),
                    dedupe_key=dedupe_key,
                    correlation_id=enriched.get("correlation_id"),
                    causation_id=enriched.get("causation_id"),
                    schema=enriched.get("schema", "genesis.event.v1")
                )
            except Exception as e:
                logger.error(f"❌ Event persistence failed (continuing): {e}")
            
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
    
    async def _emit_blocked_event(self, original_topic: str, event: Dict[str, Any], reason: str):
        """Emit audit event for blocked action (bypasses guardians)"""
        try:
            audit_event = {
                "id": f"blocked-{event.get('id', 'unknown')}",
                "type": "guardians.action_blocked",
                "source": "security.guardians",
                "original_topic": original_topic,
                "blocked_event": event,
                "reason": reason,
                "_genesis_timestamp": datetime.now(UTC).isoformat().replace('+00:00', 'Z'),
            }
            
            # Directly notify subscribers without re-checking guardians
            subscribers = self._subs.get("security.guardians.action.blocked", [])
            for sub in subscribers:
                try:
                    result = sub(audit_event)
                    if asyncio.iscoroutine(result):
                        await result
                except Exception as ex:
                    logger.error(f"❌ Failed to emit blocked event audit: {ex}")
        except Exception as e:
            logger.error(f"❌ Failed to create blocked event audit: {e}")
    
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


def ensure_topic(topic: str) -> None:
    """
    Ensure a topic is registered in the Genesis bus.
    Used to dynamically add topics that may not be in the initial registry.
    
    Args:
        topic: Topic name to ensure exists
    """
    if topic not in genesis_bus._valid_topics:
        genesis_bus._valid_topics.add(topic)
        logger.debug(f"📡 Genesis topic registered: {topic}")


# One-time ARIE integrity hook (triggered on deployment)
if os.getenv("ARIE_ENABLED", "false").lower() == "true" and os.getenv("GENESIS_ACTIVE", "false").lower() == "true":
    try:
        from bridge_backend.engines.arie.core import ARIEEngine
        from bridge_backend.engines.arie.models import PolicyType
        
        logger.info("🔧 Genesis: ARIE one-time integrity hook activated")
        
        # Run ARIE with SAFE_EDIT policy
        engine = ARIEEngine()
        policy_str = os.getenv("ARIE_POLICY", "SAFE_EDIT")
        policy = PolicyType(policy_str)
        
        summary = engine.run(policy=policy, dry_run=False, apply=True)
        
        logger.info(f"✅ ARIE one-time run complete: {summary.findings_count} findings, {summary.fixes_applied} fixes applied")
        
        # Publish results to Genesis bus
        asyncio.run(genesis_bus.publish("arie.audit", {
            "id": f"arie-genesis-{summary.run_id}",
            "type": "arie.genesis_hook_complete",
            "source": "arie.genesis_hook",
            "run_id": summary.run_id,
            "findings_count": summary.findings_count,
            "fixes_applied": summary.fixes_applied,
            "policy": policy.value,
        }))
        
    except Exception as e:
        logger.error(f"❌ ARIE genesis hook failed: {e}")
        # Don't fail deployment if ARIE fails
        pass
