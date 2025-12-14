"""
Umbra Triage Mesh Core
Real-time triage fabric with correlation, classification, and decision engine
"""

import logging
import os
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict

from .models import (
    TriageTicket, Incident, HealPlan, Report, TriageSeverity, 
    TriageStatus, TriageKind, HealAction
)

logger = logging.getLogger(__name__)


class UmbraTriageCore:
    """
    Unified Triage Mesh Core
    
    Pipelines:
    - collect: Ingest signals from various sources
    - correlate: Group related signals
    - classify: Determine severity and type
    - decide: Generate heal plan
    - heal: Delegate to healers (via Autonomy/Cascade)
    - certify: Truth certification
    - report: Generate reports
    """
    
    def __init__(self):
        self.enabled = os.getenv("UMBRA_ENABLED", "true").lower() == "true"
        self.allow_heal = os.getenv("UMBRA_ALLOW_HEAL", "false").lower() == "true"
        self.parity_strict = os.getenv("UMBRA_PARITY_STRICT", "true").lower() == "true"
        self.error_threshold = int(os.getenv("UMBRA_HEALTH_ERROR_THRESHOLD", "5"))
        self.warn_threshold = int(os.getenv("UMBRA_HEALTH_WARN_THRESHOLD", "2"))
        
        # In-memory storage for tickets (in production, use persistent storage)
        self.tickets: Dict[str, TriageTicket] = {}
        self.incidents: List[Incident] = []
        self.reports: List[Report] = []
        
        # Correlation graph: tracks relationships between incidents
        self.correlation_graph: Dict[str, List[str]] = defaultdict(list)
        
        logger.info(f"[Umbra Triage] Initialized (enabled={self.enabled}, allow_heal={self.allow_heal})")
    
    async def ingest_signal(self, signal: Dict[str, Any]) -> Optional[Incident]:
        """
        Collect and process a signal from external source
        
        Args:
            signal: Signal data with keys: kind, source, message, metadata, severity
            
        Returns:
            Created incident or None
        """
        if not self.enabled:
            logger.warning("[Umbra Triage] Disabled, ignoring signal")
            return None
        
        try:
            # Create incident from signal
            incident = Incident(
                incident_id=f"INC-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}-{len(self.incidents)}",
                kind=TriageKind(signal.get("kind", "runtime")),
                severity=TriageSeverity(signal.get("severity", "info")),
                source=signal.get("source", "unknown"),
                message=signal.get("message", ""),
                metadata=signal.get("metadata", {}),
                timestamp=datetime.utcnow()
            )
            
            self.incidents.append(incident)
            logger.info(f"[Umbra Triage] Ingested signal: {incident.incident_id} ({incident.kind}/{incident.severity})")
            
            # Trigger correlation
            await self._correlate_incident(incident)
            
            return incident
            
        except Exception as e:
            logger.error(f"[Umbra Triage] Failed to ingest signal: {e}")
            return None
    
    async def _correlate_incident(self, incident: Incident):
        """
        Correlate incident with existing tickets or create new ticket
        """
        # Look for existing open tickets with similar characteristics
        matching_ticket = None
        
        for ticket in self.tickets.values():
            if ticket.status == TriageStatus.OPEN and self._is_related(incident, ticket):
                matching_ticket = ticket
                break
        
        if matching_ticket:
            # Add to existing ticket
            matching_ticket.incidents.append(incident)
            matching_ticket.updated_at = datetime.utcnow()
            
            # Update severity if incident is more severe
            if self._severity_level(incident.severity) > self._severity_level(matching_ticket.severity):
                matching_ticket.severity = incident.severity
            
            logger.info(f"[Umbra Triage] Correlated to existing ticket: {matching_ticket.ticket_id}")
        else:
            # Create new ticket
            ticket = await self._create_ticket(incident)
            logger.info(f"[Umbra Triage] Created new ticket: {ticket.ticket_id}")
    
    def _is_related(self, incident: Incident, ticket: TriageTicket) -> bool:
        """
        Determine if incident is related to ticket
        
        Correlation rules:
        - Same kind and source
        - Within time window (5 minutes)
        - Similar signals
        """
        if incident.kind != ticket.kind:
            return False
        
        if incident.source != ticket.source:
            return False
        
        # Check time window
        time_diff = datetime.utcnow() - ticket.created_at
        if time_diff > timedelta(minutes=5):
            return False
        
        return True
    
    def _severity_level(self, severity: TriageSeverity) -> int:
        """Convert severity to numeric level for comparison"""
        levels = {
            TriageSeverity.INFO: 0,
            TriageSeverity.WARNING: 1,
            TriageSeverity.HIGH: 2,
            TriageSeverity.CRITICAL: 3
        }
        return levels.get(severity, 0)
    
    async def _create_ticket(self, incident: Incident) -> TriageTicket:
        """Create a new triage ticket"""
        ticket_id = f"UM-{datetime.utcnow().strftime('%Y-%m-%d')}-{len(self.tickets):04d}"
        
        ticket = TriageTicket(
            ticket_id=ticket_id,
            kind=incident.kind,
            source=incident.source,
            signals=[str(incident.kind)],
            severity=incident.severity,
            incidents=[incident],
            status=TriageStatus.OPEN,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        self.tickets[ticket_id] = ticket
        
        # Emit event to Genesis
        await self._emit_ticket_event("triage.ticket.open", ticket)
        
        return ticket
    
    async def classify_and_decide(self, ticket_id: str) -> Optional[HealPlan]:
        """
        Classify ticket and generate heal plan
        
        Args:
            ticket_id: Ticket to classify
            
        Returns:
            Generated heal plan or None
        """
        ticket = self.tickets.get(ticket_id)
        if not ticket:
            logger.error(f"[Umbra Triage] Ticket not found: {ticket_id}")
            return None
        
        # Generate heal plan based on ticket characteristics
        plan = await self._generate_heal_plan(ticket)
        
        if plan:
            ticket.heal_plan = plan
            ticket.updated_at = datetime.utcnow()
            logger.info(f"[Umbra Triage] Generated heal plan: {plan.plan_id}")
            
            # Emit event
            await self._emit_heal_event("triage.heal.intent", plan)
        
        return plan
    
    async def _generate_heal_plan(self, ticket: TriageTicket) -> Optional[HealPlan]:
        """
        Generate heal plan based on ticket classification
        """
        plan_id = f"PLAN-{ticket.ticket_id}"
        
        actions: List[HealAction] = []
        parity_prechecks: List[str] = []
        
        # Classify based on kind and source
        if ticket.kind == TriageKind.DEPLOY:
            if "netlify" in ticket.source.lower():
                actions.append(HealAction(
                    action_type="normalize_netlify_config",
                    target="netlify.toml",
                    parameters={"check_headers": True, "check_redirects": True}
                ))
                parity_prechecks.append("env:netlify/render")
            elif "render" in ticket.source.lower():
                actions.append(HealAction(
                    action_type="normalize_render_config",
                    target="render.yaml",
                    parameters={"check_cors": True, "check_env": True}
                ))
                parity_prechecks.append("env:render/netlify")
        
        elif ticket.kind == TriageKind.API or ticket.kind == TriageKind.ENDPOINT:
            actions.append(HealAction(
                action_type="endpoint_health_check",
                target="api_endpoints",
                parameters={"verify_routes": True}
            ))
        
        elif ticket.kind == TriageKind.RUNTIME:
            actions.append(HealAction(
                action_type="service_restart",
                target="runtime_service",
                parameters={"graceful": True}
            ))
        
        if not actions:
            logger.warning(f"[Umbra Triage] No actions generated for {ticket.ticket_id}")
            return None
        
        plan = HealPlan(
            plan_id=plan_id,
            ticket_id=ticket.ticket_id,
            actions=actions,
            parity_prechecks=parity_prechecks,
            truth_policy="standard",
            created_at=datetime.utcnow()
        )
        
        return plan
    
    async def run_sweep(self, timeout: int = 90) -> Report:
        """
        Run a complete triage sweep
        
        Args:
            timeout: Timeout in seconds
            
        Returns:
            Report with results
        """
        start_time = datetime.utcnow()
        logger.info("[Umbra Triage] Starting sweep...")
        
        report_id = f"REP-{start_time.strftime('%Y%m%d-%H%M%S')}"
        
        # Collect metrics
        open_tickets = [t for t in self.tickets.values() if t.status == TriageStatus.OPEN]
        critical_tickets = [t for t in open_tickets if t.severity == TriageSeverity.CRITICAL]
        warning_tickets = [t for t in open_tickets if t.severity == TriageSeverity.WARNING]
        
        # Generate heal plans for open tickets without plans
        plans_generated = 0
        for ticket in open_tickets:
            if not ticket.heal_plan:
                plan = await self.classify_and_decide(ticket.ticket_id)
                if plan:
                    plans_generated += 1
        
        duration = (datetime.utcnow() - start_time).total_seconds()
        
        report = Report(
            report_id=report_id,
            run_timestamp=start_time,
            tickets_opened=len(open_tickets),
            tickets_healed=0,  # Would be updated after healing
            tickets_failed=0,
            critical_count=len(critical_tickets),
            warning_count=len(warning_tickets),
            heal_plans_generated=plans_generated,
            heal_plans_applied=0,  # Would be updated after healing
            duration_seconds=duration,
            summary=f"Sweep complete: {len(open_tickets)} open tickets, {plans_generated} plans generated",
            tickets=list(self.tickets.values())
        )
        
        self.reports.append(report)
        
        # Save report to file
        await self._save_report(report)
        
        logger.info(f"[Umbra Triage] Sweep complete: {report.summary}")
        
        return report
    
    async def _save_report(self, report: Report):
        """Save report to file system"""
        try:
            import json
            from pathlib import Path
            
            reports_dir = Path("/home/runner/work/SR-AIbridge-/SR-AIbridge-/bridge_backend/logs/umbra_reports")
            reports_dir.mkdir(parents=True, exist_ok=True)
            
            # Save as timestamped file
            report_file = reports_dir / f"{report.report_id}.json"
            with open(report_file, "w") as f:
                json.dump(report.dict(), f, indent=2, default=str)
            
            # Also save as latest
            latest_file = reports_dir / "latest.json"
            with open(latest_file, "w") as f:
                json.dump(report.dict(), f, indent=2, default=str)
            
            logger.info(f"[Umbra Triage] Report saved: {report_file}")
            
        except Exception as e:
            logger.error(f"[Umbra Triage] Failed to save report: {e}")
    
    async def _emit_ticket_event(self, topic: str, ticket: TriageTicket):
        """Emit ticket event to Genesis bus"""
        try:
            from bridge_backend.genesis.bus import genesis_bus
            
            if genesis_bus.is_enabled():
                await genesis_bus.publish(topic, {
                    "ticket_id": ticket.ticket_id,
                    "kind": ticket.kind,
                    "severity": ticket.severity,
                    "status": ticket.status,
                    "source": ticket.source,
                    "timestamp": ticket.updated_at.isoformat()
                })
        except Exception as e:
            logger.warning(f"[Umbra Triage] Failed to emit ticket event: {e}")
    
    async def _emit_heal_event(self, topic: str, plan: HealPlan):
        """Emit heal event to Genesis bus"""
        try:
            from bridge_backend.genesis.bus import genesis_bus
            
            if genesis_bus.is_enabled():
                await genesis_bus.publish(topic, {
                    "plan_id": plan.plan_id,
                    "ticket_id": plan.ticket_id,
                    "actions": [a.dict() for a in plan.actions],
                    "parity_prechecks": plan.parity_prechecks,
                    "certified": plan.certified,
                    "timestamp": plan.created_at.isoformat()
                })
        except Exception as e:
            logger.warning(f"[Umbra Triage] Failed to emit heal event: {e}")
    
    def get_ticket(self, ticket_id: str) -> Optional[TriageTicket]:
        """Get ticket by ID"""
        return self.tickets.get(ticket_id)
    
    def list_tickets(self, status: Optional[TriageStatus] = None) -> List[TriageTicket]:
        """List tickets, optionally filtered by status"""
        tickets = list(self.tickets.values())
        
        if status:
            tickets = [t for t in tickets if t.status == status]
        
        # Sort by created_at descending
        tickets.sort(key=lambda t: t.created_at, reverse=True)
        
        return tickets
    
    def get_latest_report(self) -> Optional[Report]:
        """Get the most recent report"""
        if not self.reports:
            return None
        return self.reports[-1]
