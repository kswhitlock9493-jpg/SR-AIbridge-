"""
Umbra Triage Mesh - Blueprint Link Adapter
Registers triage ticket schema with Blueprint Engine
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


async def register_triage_schema():
    """
    Register Umbra triage ticket schema with Blueprint Engine
    """
    try:
        from bridge_backend.bridge_core.engines.blueprint.service import BlueprintEngine
        
        blueprint = BlueprintEngine()
        
        # Define triage ticket schema
        schema = {
            "name": "triage_ticket",
            "version": "1.0.0",
            "description": "Umbra Triage Mesh ticket schema",
            "fields": {
                "ticket_id": {
                    "type": "string",
                    "required": True,
                    "description": "Unique ticket identifier"
                },
                "kind": {
                    "type": "enum",
                    "values": ["build", "deploy", "runtime", "api", "endpoint", "webhook"],
                    "required": True,
                    "description": "Type of triage issue"
                },
                "source": {
                    "type": "string",
                    "required": True,
                    "description": "Source system (render, netlify, github, etc.)"
                },
                "severity": {
                    "type": "enum",
                    "values": ["critical", "high", "warning", "info"],
                    "required": True,
                    "description": "Severity level"
                },
                "status": {
                    "type": "enum",
                    "values": ["open", "in_progress", "healed", "closed", "failed"],
                    "required": True,
                    "description": "Ticket status"
                },
                "signals": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of signal types"
                },
                "incidents": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "Correlated incidents"
                },
                "heal_plan": {
                    "type": "object",
                    "required": False,
                    "description": "Associated heal plan"
                },
                "created_at": {
                    "type": "datetime",
                    "required": True
                },
                "updated_at": {
                    "type": "datetime",
                    "required": True
                },
                "healed_at": {
                    "type": "datetime",
                    "required": False
                },
                "closed_at": {
                    "type": "datetime",
                    "required": False
                }
            }
        }
        
        # Register schema
        await blueprint.register_schema("triage_ticket", schema)
        
        logger.info("[Umbra Blueprint Link] Triage ticket schema registered")
        
        return {"ok": True, "schema": "triage_ticket"}
    
    except ImportError:
        logger.warning("[Umbra Blueprint Link] Blueprint engine not available")
        return {"ok": False, "reason": "blueprint_engine_unavailable"}
    except Exception as e:
        logger.error(f"[Umbra Blueprint Link] Failed to register schema: {e}")
        return {"ok": False, "error": str(e)}


async def validate_ticket(ticket: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate ticket against Blueprint schema
    
    Args:
        ticket: Ticket data to validate
        
    Returns:
        Validation result
    """
    try:
        from bridge_backend.bridge_core.engines.blueprint.service import BlueprintEngine
        
        blueprint = BlueprintEngine()
        
        # Validate against schema
        result = await blueprint.validate("triage_ticket", ticket)
        
        if result.get("valid"):
            logger.debug(f"[Umbra Blueprint Link] Ticket validation passed: {ticket.get('ticket_id')}")
        else:
            logger.warning(f"[Umbra Blueprint Link] Ticket validation failed: {result.get('errors')}")
        
        return result
    
    except ImportError:
        logger.debug("[Umbra Blueprint Link] Blueprint engine not available, skipping validation")
        return {"valid": True, "reason": "blueprint_engine_unavailable"}
    except Exception as e:
        logger.error(f"[Umbra Blueprint Link] Validation error: {e}")
        return {"valid": False, "error": str(e)}


async def emit_schema_event(event_type: str, data: Dict[str, Any]):
    """
    Emit schema event to Genesis bus
    
    Args:
        event_type: Event type
        data: Event data
    """
    try:
        from bridge_backend.genesis.bus import genesis_bus
        
        if not genesis_bus.is_enabled():
            return
        
        await genesis_bus.publish(f"triage.schema.{event_type}", {
            **data,
            "source": "umbra_triage"
        })
        
        logger.debug(f"[Umbra Blueprint Link] Emitted event: triage.schema.{event_type}")
    
    except Exception as e:
        logger.warning(f"[Umbra Blueprint Link] Failed to emit event: {e}")
