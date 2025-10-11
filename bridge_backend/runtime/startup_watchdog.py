#!/usr/bin/env python3
"""
Startup Watchdog for SR-AIbridge v1.9.6g
Monitors startup latency with adaptive thresholds and predictive stabilizer integration
"""
import os
import time
import logging
import datetime
from dateutil.tz import tzutc
from bridge_backend.runtime.predictive_stabilizer import (
    record_startup_metrics,
    archive_old_tickets,
    aggregate_to_daily_report
)

log = logging.getLogger(__name__)

# Default tolerance (used as fallback when no adaptive threshold available)
BIND_LATENCY_TOLERANCE = 6.0  # seconds
TICKET_DIR = "bridge_backend/diagnostics/stabilization_tickets"

class StartupWatchdog:
    """Monitors startup process with adaptive thresholds"""
    
    def __init__(self):
        self.boot_start = time.time()
        self.port_resolved_at = None
        self.bind_confirmed_at = None
        self.heartbeat_initialized_at = None
        self.db_synced_at = None
        
        # Run cleanup on initialization
        try:
            archive_old_tickets()
        except Exception as e:
            log.warning(f"[STABILIZER] Failed to archive old tickets: {e}")
        
    def mark_port_resolved(self, port: int):
        """Record when PORT was resolved"""
        self.port_resolved_at = time.time()
        elapsed = self.port_resolved_at - self.boot_start
        log.info(f"[BOOT] PORT resolved in {elapsed:.2f}s -> {port}")
        
    def mark_bind_confirmed(self):
        """Record when Uvicorn confirmed binding"""
        self.bind_confirmed_at = time.time()
        elapsed = self.bind_confirmed_at - self.boot_start
        log.info(f"[BOOT] Adaptive port bind: success in {elapsed:.2f}s")
        
        # Delegate to predictive stabilizer for adaptive threshold checking
        try:
            port = int(os.getenv("PORT", "8000"))
            record_startup_metrics(
                latency=elapsed,
                port=port,
                port_resolution_time=self.port_resolved_at - self.boot_start if self.port_resolved_at else None
            )
        except Exception as e:
            log.warning(f"[STABILIZER] Failed to record startup metrics: {e}")
            
    def mark_heartbeat_initialized(self):
        """Record when heartbeat was initialized"""
        self.heartbeat_initialized_at = time.time()
        elapsed = self.heartbeat_initialized_at - self.boot_start
        log.info(f"[HEARTBEAT] ✅ Live (initialized in {elapsed:.2f}s)")
        
        # Set environment marker for is_live() check
        os.environ["HEARTBEAT_INITIALIZED"] = "1"
        
    def mark_db_synced(self):
        """Record when DB schema sync completed"""
        self.db_synced_at = time.time()
        elapsed = self.db_synced_at - self.boot_start
        log.info(f"[DB] Schema sync completed in {elapsed:.2f}s")
        
    def finalize_boot(self):
        """Called when boot sequence is complete"""
        try:
            aggregate_to_daily_report()
        except Exception as e:
            log.warning(f"[STABILIZER] Failed to generate daily report: {e}")
        
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

# Global watchdog instance
watchdog = StartupWatchdog()
