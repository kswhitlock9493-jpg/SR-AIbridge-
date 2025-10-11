#!/usr/bin/env python3
"""
Startup Watchdog for SR-AIbridge v1.9.6f
Monitors startup latency and creates diagnostic tickets for abnormal patterns
"""
import os
import time
import logging
import datetime
from dateutil.tz import tzutc

log = logging.getLogger(__name__)

# Tolerances
BIND_LATENCY_TOLERANCE = 6.0  # seconds
TICKET_DIR = "bridge_backend/diagnostics/stabilization_tickets"

class StartupWatchdog:
    """Monitors startup process and detects anomalies"""
    
    def __init__(self):
        self.boot_start = time.time()
        self.port_resolved_at = None
        self.bind_confirmed_at = None
        self.heartbeat_initialized_at = None
        self.db_synced_at = None
        
    def mark_port_resolved(self, port: int):
        """Record when PORT was resolved"""
        self.port_resolved_at = time.time()
        elapsed = self.port_resolved_at - self.boot_start
        log.info(f"[STABILIZER] PORT resolved in {elapsed:.2f}s -> {port}")
        
    def mark_bind_confirmed(self):
        """Record when Uvicorn confirmed binding"""
        self.bind_confirmed_at = time.time()
        elapsed = self.bind_confirmed_at - self.boot_start
        log.info(f"[STABILIZER] Bind confirmed in {elapsed:.2f}s")
        
        # Check if bind latency exceeded tolerance
        if elapsed > BIND_LATENCY_TOLERANCE:
            self._create_latency_ticket(elapsed)
            
    def mark_heartbeat_initialized(self):
        """Record when heartbeat was initialized"""
        self.heartbeat_initialized_at = time.time()
        elapsed = self.heartbeat_initialized_at - self.boot_start
        log.info(f"[STABILIZER] Heartbeat initialized in {elapsed:.2f}s")
        
    def mark_db_synced(self):
        """Record when DB schema sync completed"""
        self.db_synced_at = time.time()
        elapsed = self.db_synced_at - self.boot_start
        log.info(f"[STABILIZER] DB sync completed in {elapsed:.2f}s")
        
    def get_metrics(self) -> dict:
        """Return startup metrics"""
        current = time.time()
        return {
            "total_startup_time": current - self.boot_start,
            "port_resolution_time": self.port_resolved_at - self.boot_start if self.port_resolved_at else None,
            "bind_time": self.bind_confirmed_at - self.boot_start if self.bind_confirmed_at else None,
            "heartbeat_init_time": self.heartbeat_initialized_at - self.boot_start if self.heartbeat_initialized_at else None,
            "db_sync_time": self.db_synced_at - self.boot_start if self.db_synced_at else None,
        }
        
    def _create_latency_ticket(self, latency: float):
        """Create diagnostic ticket for excessive startup latency"""
        os.makedirs(TICKET_DIR, exist_ok=True)
        
        timestamp = datetime.datetime.now(tzutc()).strftime("%Y%m%dT%H%M%SZ")
        ticket_name = f"{timestamp}_startup_bind.md"
        ticket_path = os.path.join(TICKET_DIR, ticket_name)
        
        metrics = self.get_metrics()
        
        md_content = [
            "# Startup Latency Stabilization Ticket\n",
            f"**Detected:** {timestamp}\n",
            f"**Bind Latency:** {latency:.2f}s (tolerance: {BIND_LATENCY_TOLERANCE}s)\n",
            "\n## Metrics\n",
            f"- Port resolution: {metrics['port_resolution_time']:.2f}s" if metrics['port_resolution_time'] else "- Port resolution: pending",
            f"- Bind confirmation: {metrics['bind_time']:.2f}s" if metrics['bind_time'] else "- Bind confirmation: pending",
            f"- DB sync: {metrics['db_sync_time']:.2f}s" if metrics['db_sync_time'] else "- DB sync: pending",
            f"- Heartbeat init: {metrics['heartbeat_init_time']:.2f}s" if metrics['heartbeat_init_time'] else "- Heartbeat init: pending",
            "\n## Recommended Actions\n",
            "- Review Render build logs for delayed PORT injection",
            "- Check for blocking operations in startup sequence",
            "- Verify database connection pool initialization time",
            "- Consider async initialization for non-critical components",
            "- Monitor for false 'Application shutdown complete' triggers",
        ]
        
        try:
            with open(ticket_path, "w") as f:
                f.write("\n".join(md_content))
            log.warning(f"[STABILIZER] ⚠️ Latency ticket created: {ticket_path}")
        except Exception as e:
            log.error(f"[STABILIZER] Failed to create latency ticket: {e}")

# Global watchdog instance
watchdog = StartupWatchdog()
