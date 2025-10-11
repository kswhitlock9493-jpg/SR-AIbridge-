"""
Genesis Universal Adapters
Convenience helpers for publishing Genesis events with type safety
"""
from typing import Dict, Any, Optional
import logging
from .contracts import GenesisEvent, EventKind
from .bus import genesis_bus

logger = logging.getLogger(__name__)


async def publish(
    kind: str,
    topic: str,
    source: str,
    payload: Dict[str, Any],
    correlation_id: Optional[str] = None,
    causation_id: Optional[str] = None,
    dedupe_key: Optional[str] = None,
    schema: str = "genesis.event.v1"
) -> Optional[str]:
    """
    Publish a Genesis event
    
    Args:
        kind: Event kind (intent, heal, fact, audit, metric, control)
        topic: Event topic (e.g. "engine.truth.fact.created")
        source: Source identifier (e.g. "engine.truth")
        payload: Event data
        correlation_id: Optional correlation ID
        causation_id: Optional causation ID
        dedupe_key: Optional idempotency key
        schema: Schema version
    
    Returns:
        Event ID if published successfully, None otherwise
    """
    try:
        event = GenesisEvent(
            topic=topic,
            source=source,
            kind=kind,
            payload=payload,
            correlation_id=correlation_id,
            causation_id=causation_id,
            dedupe_key=dedupe_key,
            schema=schema
        )
        
        # Publish to bus
        await genesis_bus.publish(topic, event.model_dump())
        
        logger.debug(f"📡 Published {kind} event: {topic} from {source}")
        return event.id
    
    except Exception as e:
        logger.error(f"❌ Failed to publish {kind} event {topic}: {e}")
        return None


async def emit_intent(
    topic: str,
    source: str,
    payload: Dict[str, Any],
    **kwargs
) -> Optional[str]:
    """
    Emit an intent event
    
    Intent events signal cross-engine action requests or proposals.
    
    Example:
        await emit_intent(
            topic="engine.truth.fact.created",
            source="engine.truth",
            payload={"subject": "mission/42", "claim": "jobs-indexed"}
        )
    """
    return await publish(kind=EventKind.INTENT, topic=topic, source=source, payload=payload, **kwargs)


async def emit_heal(
    topic: str,
    source: str,
    payload: Dict[str, Any],
    **kwargs
) -> Optional[str]:
    """
    Emit a heal event
    
    Heal events trigger self-repair or request intervention.
    
    Example:
        await emit_heal(
            topic="runtime.health.degraded",
            source="runtime.health",
            payload={"component": "database", "status": "degraded"}
        )
    """
    return await publish(kind=EventKind.HEAL, topic=topic, source=source, payload=payload, **kwargs)


async def emit_fact(
    topic: str,
    source: str,
    payload: Dict[str, Any],
    **kwargs
) -> Optional[str]:
    """
    Emit a fact event
    
    Fact events certify immutable truths for cross-engine synchronization.
    
    Example:
        await emit_fact(
            topic="engine.truth.fact.certified",
            source="engine.truth",
            payload={"fact_id": "fact-123", "confidence": 0.98}
        )
    """
    return await publish(kind=EventKind.FACT, topic=topic, source=source, payload=payload, **kwargs)


async def emit_audit(
    topic: str,
    source: str,
    payload: Dict[str, Any],
    **kwargs
) -> Optional[str]:
    """
    Emit an audit event
    
    Audit events track security, compliance, and access control.
    
    Example:
        await emit_audit(
            topic="security.guardians.action.blocked",
            source="guardians",
            payload={"action": "destructive_op", "reason": "policy_violation"}
        )
    """
    return await publish(kind=EventKind.AUDIT, topic=topic, source=source, payload=payload, **kwargs)


async def emit_metric(
    topic: str,
    source: str,
    payload: Dict[str, Any],
    **kwargs
) -> Optional[str]:
    """
    Emit a metric event
    
    Metric events capture performance, usage, and telemetry data.
    
    Example:
        await emit_metric(
            topic="runtime.metrics.latency",
            source="runtime.metrics",
            payload={"endpoint": "/api/missions", "latency_ms": 45.2}
        )
    """
    return await publish(kind=EventKind.METRIC, topic=topic, source=source, payload=payload, **kwargs)


async def emit_control(
    topic: str,
    source: str,
    payload: Dict[str, Any],
    **kwargs
) -> Optional[str]:
    """
    Emit a control event
    
    Control events manage deploy orchestration and configuration.
    
    Example:
        await emit_control(
            topic="deploy.tde.stage.started",
            source="deploy.tde",
            payload={"stage": "warm_caches", "attempt": 1}
        )
    """
    return await publish(kind=EventKind.CONTROL, topic=topic, source=source, payload=payload, **kwargs)


# Convenience helpers for common patterns

async def health_degraded(component: str, details: Dict[str, Any]) -> Optional[str]:
    """
    Report degraded health for a component
    
    Args:
        component: Component name (e.g. "database", "cache")
        details: Health status details
    """
    return await emit_heal(
        topic=f"runtime.health.{component}.degraded",
        source="runtime.health",
        payload={**details, "component": component}
    )


async def deploy_failed(stage: str, details: Dict[str, Any]) -> Optional[str]:
    """
    Report deploy stage failure
    
    Args:
        stage: Stage name (e.g. "warm_caches", "post_boot")
        details: Failure details
    """
    return await emit_heal(
        topic=f"deploy.tde.{stage}.failed",
        source="deploy.tde",
        payload={**details, "stage": stage}
    )


async def deploy_stage_started(stage: str, details: Optional[Dict[str, Any]] = None) -> Optional[str]:
    """
    Report deploy stage started
    
    Args:
        stage: Stage name
        details: Optional stage details
    """
    return await emit_control(
        topic=f"deploy.tde.stage.started",
        source="deploy.tde",
        payload={**(details or {}), "stage": stage}
    )


async def deploy_stage_completed(stage: str, details: Optional[Dict[str, Any]] = None) -> Optional[str]:
    """
    Report deploy stage completed
    
    Args:
        stage: Stage name
        details: Optional stage details
    """
    return await emit_control(
        topic=f"deploy.tde.stage.completed",
        source="deploy.tde",
        payload={**(details or {}), "stage": stage}
    )
