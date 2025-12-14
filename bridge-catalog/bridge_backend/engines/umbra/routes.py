"""
Umbra Triage Mesh Routes
REST API endpoints for unified triage system
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import logging

from .core import UmbraTriageCore
from .healers import UmbraHealers
from .models import TriageStatus, TriageSeverity, TriageKind

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/umbra", tags=["umbra-triage"])

# Singleton instances
_triage_core: Optional[UmbraTriageCore] = None
_healers: Optional[UmbraHealers] = None


def get_triage_core() -> UmbraTriageCore:
    """Get or create triage core instance"""
    global _triage_core
    if _triage_core is None:
        _triage_core = UmbraTriageCore()
    return _triage_core


def get_healers() -> UmbraHealers:
    """Get or create healers instance"""
    global _healers
    if _healers is None:
        _healers = UmbraHealers()
    return _healers


# Request models
class SignalInput(BaseModel):
    kind: str
    source: str
    message: str
    severity: str = "info"
    metadata: Dict[str, Any] = {}


class TicketActionInput(BaseModel):
    action: str  # close, heal, etc.


# === Status & Info Endpoints ===

@router.get("/status")
async def get_status():
    """Get Umbra Triage Mesh status"""
    core = get_triage_core()
    healers = get_healers()
    
    return {
        "status": "active" if core.enabled else "disabled",
        "version": "1.9.7k",
        "enabled": core.enabled,
        "allow_heal": healers.allow_heal,
        "auto_heal_on": healers.auto_heal_on,
        "parity_strict": core.parity_strict,
        "error_threshold": core.error_threshold,
        "warn_threshold": core.warn_threshold,
        "stats": {
            "total_tickets": len(core.tickets),
            "open_tickets": len([t for t in core.tickets.values() if t.status == TriageStatus.OPEN]),
            "total_incidents": len(core.incidents),
            "total_reports": len(core.reports)
        }
    }


# === Signal Ingestion ===

@router.post("/signal")
async def ingest_signal(signal: SignalInput):
    """
    Ingest a signal from external source
    
    **RBAC**: Admiral, Captain
    """
    core = get_triage_core()
    
    try:
        incident = await core.ingest_signal(signal.dict())
        
        if not incident:
            raise HTTPException(status_code=503, detail="Umbra disabled or failed to process signal")
        
        return {
            "status": "ingested",
            "incident_id": incident.incident_id,
            "incident": incident.dict()
        }
    except Exception as e:
        logger.error(f"[Umbra Triage API] Signal ingestion error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# === Tickets Management ===

@router.get("/tickets")
async def list_tickets(status: Optional[str] = None):
    """
    List triage tickets
    
    **RBAC**: Admiral, Captain, Observer
    """
    core = get_triage_core()
    
    try:
        ticket_status = TriageStatus(status) if status else None
        tickets = core.list_tickets(status=ticket_status)
        
        return {
            "count": len(tickets),
            "tickets": [t.dict() for t in tickets]
        }
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
    except Exception as e:
        logger.error(f"[Umbra Triage API] List tickets error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tickets/{ticket_id}")
async def get_ticket(ticket_id: str):
    """
    Get ticket details
    
    **RBAC**: Admiral, Captain, Observer
    """
    core = get_triage_core()
    
    ticket = core.get_ticket(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail=f"Ticket not found: {ticket_id}")
    
    return ticket.dict()


@router.post("/tickets/{ticket_id}/action")
async def ticket_action(ticket_id: str, action: TicketActionInput):
    """
    Perform action on ticket (close, heal, etc.)
    
    **RBAC**: Admiral only
    """
    core = get_triage_core()
    healers = get_healers()
    
    ticket = core.get_ticket(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail=f"Ticket not found: {ticket_id}")
    
    try:
        if action.action == "close":
            ticket.status = TriageStatus.CLOSED
            from datetime import datetime
            ticket.closed_at = datetime.utcnow()
            
            return {
                "status": "closed",
                "ticket_id": ticket_id
            }
        
        elif action.action == "heal":
            # Generate heal plan if not exists
            if not ticket.heal_plan:
                plan = await core.classify_and_decide(ticket_id)
                if not plan:
                    raise HTTPException(status_code=400, detail="Unable to generate heal plan")
            
            # Execute heal plan
            result = await healers.execute_heal_plan(ticket.heal_plan, ticket)
            
            return {
                "status": "heal_executed",
                "ticket_id": ticket_id,
                "result": result
            }
        
        else:
            raise HTTPException(status_code=400, detail=f"Unknown action: {action.action}")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Umbra Triage API] Ticket action error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# === Triage Sweep ===

@router.post("/run")
async def run_triage_sweep(timeout: int = 90, heal: bool = False):
    """
    Run a complete triage sweep
    
    **RBAC**: Admiral only
    
    Args:
        timeout: Timeout in seconds
        heal: Whether to execute heal plans
    """
    core = get_triage_core()
    healers = get_healers()
    
    try:
        # Run sweep
        report = await core.run_sweep(timeout=timeout)
        
        # Execute healing if requested and allowed
        if heal and healers.allow_heal:
            logger.info("[Umbra Triage API] Executing heal plans...")
            
            healed_count = 0
            failed_count = 0
            
            for ticket in report.tickets:
                if ticket.status == TriageStatus.OPEN and ticket.heal_plan:
                    result = await healers.execute_heal_plan(ticket.heal_plan, ticket)
                    
                    if result.get("status") == "success":
                        healed_count += 1
                    else:
                        failed_count += 1
            
            # Update report
            report.tickets_healed = healed_count
            report.tickets_failed = failed_count
            report.heal_plans_applied = healed_count
            
            logger.info(f"[Umbra Triage API] Healing complete: {healed_count} healed, {failed_count} failed")
        
        return {
            "status": "complete",
            "report": report.dict()
        }
    
    except Exception as e:
        logger.error(f"[Umbra Triage API] Run sweep error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# === Reports ===

@router.get("/reports")
async def list_reports(limit: int = 10):
    """
    List triage reports
    
    **RBAC**: Admiral, Captain, Observer
    """
    core = get_triage_core()
    
    reports = core.reports[-limit:]  # Get last N reports
    
    return {
        "count": len(reports),
        "reports": [r.dict() for r in reports]
    }


@router.get("/reports/latest")
async def get_latest_report():
    """
    Get the most recent triage report
    
    **RBAC**: Admiral, Captain, Observer
    """
    core = get_triage_core()
    
    report = core.get_latest_report()
    if not report:
        raise HTTPException(status_code=404, detail="No reports available")
    
    return report.dict()
