"""
Genesis Core Contract (GCC)
Typed event envelope with idempotency, versioning, and traceability
"""
from pydantic import BaseModel, Field
from typing import Literal, Optional, Dict, Any
from datetime import datetime
import uuid


class GenesisEvent(BaseModel):
    """
    Genesis Event Envelope - Universal contract for all engine communication
    
    Provides:
    - Unique identification (id, correlation_id, causation_id)
    - Temporal tracking (ts)
    - Topic-based routing (topic)
    - Source traceability (source)
    - Event classification (kind)
    - Schema versioning (schema)
    - Idempotency (dedupe_key)
    """
    
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique event identifier (UUID)"
    )
    
    ts: datetime = Field(
        default_factory=datetime.utcnow,
        description="Event timestamp (UTC)"
    )
    
    topic: str = Field(
        ...,
        description="Event topic (e.g. 'engine.truth.fact.created')",
        examples=["engine.truth.fact.created", "system.health.degraded"]
    )
    
    source: str = Field(
        ...,
        description="Engine/system name that generated the event",
        examples=["engine.truth", "runtime.health", "deploy.tde"]
    )
    
    kind: Literal["intent", "heal", "fact", "audit", "metric", "control"] = Field(
        ...,
        description="Event classification"
    )
    
    correlation_id: Optional[str] = Field(
        None,
        description="Links related events across different operations"
    )
    
    causation_id: Optional[str] = Field(
        None,
        description="ID of the event that directly caused this event"
    )
    
    schema: str = Field(
        default="genesis.event.v1",
        description="Schema version for payload structure"
    )
    
    payload: Dict[str, Any] = Field(
        default_factory=dict,
        description="Event-specific data"
    )
    
    dedupe_key: Optional[str] = Field(
        None,
        description="Idempotency key to prevent duplicate processing"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "ts": "2025-10-11T09:00:00Z",
                "topic": "engine.truth.fact.created",
                "source": "engine.truth",
                "kind": "fact",
                "correlation_id": "mission-42-analysis",
                "causation_id": "550e8400-e29b-41d4-a716-446655440001",
                "schema": "genesis.event.v1",
                "payload": {
                    "subject": "mission/42",
                    "claim": "jobs-indexed",
                    "confidence": 0.98
                },
                "dedupe_key": "mission/42#jobs-indexed"
            }
        }


# Topic namespace constants
class TopicNamespace:
    """Standard topic namespaces for Genesis events"""
    
    # Engine topics: engine.<name>.<domain>.<verb>
    ENGINE_TRUTH = "engine.truth"
    ENGINE_CASCADE = "engine.cascade"
    ENGINE_AUTONOMY = "engine.autonomy"
    ENGINE_BLUEPRINT = "engine.blueprint"
    ENGINE_SCREEN = "engine.screen"
    ENGINE_SPEECH = "engine.speech"
    ENGINE_CREATIVITY = "engine.creativity"
    ENGINE_LEVIATHAN = "engine.leviathan"
    ENGINE_INDOCTRINATION = "engine.indoctrination"
    ENGINE_AGENTS_FOUNDRY = "engine.agents_foundry"
    ENGINE_PARSER = "engine.parser"
    ENGINE_RECOVERY = "engine.recovery"
    ENGINE_FILING = "engine.filing"
    
    # System topics: system.<name>.<domain>.<verb>
    SYSTEM_LEDGER = "system.ledger"
    SYSTEM_REGISTRY = "system.registry"
    SYSTEM_GUARDIANS = "system.guardians"
    SYSTEM_CAPTAINS = "system.captains"
    SYSTEM_FLEET = "system.fleet"
    SYSTEM_CUSTODY = "system.custody"
    SYSTEM_PAYMENTS = "system.payments"
    SYSTEM_PROTOCOLS = "system.protocols"
    SYSTEM_MAS = "system.mas"
    SYSTEM_HERITAGE = "system.heritage"
    
    # Runtime topics: runtime.<name>.<domain>.<verb>
    RUNTIME_HEALTH = "runtime.health"
    RUNTIME_DEPLOY = "runtime.deploy"
    RUNTIME_METRICS = "runtime.metrics"
    
    # Security topics
    SECURITY_GUARDIANS = "security.guardians"
    
    # Deploy orchestrator topics
    DEPLOY_TDE = "deploy.tde"


# Event kind helpers
class EventKind:
    """Event kind classifications"""
    INTENT = "intent"      # Intent propagation across engines
    HEAL = "heal"          # Repair requests and confirmations
    FACT = "fact"          # Fact synchronization and certification
    AUDIT = "audit"        # Security and compliance auditing
    METRIC = "metric"      # Performance and telemetry metrics
    CONTROL = "control"    # Control plane operations (deploy, config)
