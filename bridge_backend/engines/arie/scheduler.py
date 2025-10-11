"""
ARIE Scheduler - Timed Task Handler
Autonomous 12-hour integrity scan cycle
"""

import asyncio
import os
import logging
import json
from datetime import datetime, UTC
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class ARIEScheduler:
    """
    Autonomous scheduler for ARIE integrity scans
    
    Runs on configurable intervals (default: 12 hours)
    Publishes tick and summary events to Genesis bus
    """
    
    def __init__(self, engine=None, bus=None):
        self.engine = engine
        self.bus = bus
        self.enabled = os.getenv("ARIE_SCHEDULE_ENABLED", "false").lower() == "true"
        self.interval_hours = int(os.getenv("ARIE_SCHEDULE_INTERVAL_HOURS", "12"))
        self.run_on_deploy = os.getenv("ARIE_RUN_ON_DEPLOY", "true").lower() == "true"
        self.admiral_only_apply = os.getenv("ARIE_ADMIRAL_ONLY_APPLY", "true").lower() == "true"
        self.truth_mandatory = os.getenv("ARIE_TRUTH_MANDATORY", "true").lower() == "true"
        
        self._task: Optional[asyncio.Task] = None
        self._running = False
        
        # Ensure logs directory exists
        self.logs_dir = Path(__file__).parent.parent.parent / "logs"
        self.logs_dir.mkdir(exist_ok=True)
        
        logger.info(f"[ARIE Scheduler] Initialized (enabled={self.enabled}, interval={self.interval_hours}h)")
    
    async def start(self):
        """Start the scheduler loop"""
        if not self.enabled or not self.engine:
            logger.info("[ARIE Scheduler] Not starting (disabled or no engine)")
            return
        
        if self._running:
            logger.warning("[ARIE Scheduler] Already running")
            return
        
        self._running = True
        self._task = asyncio.create_task(self._schedule_loop())
        logger.info(f"[ARIE Scheduler] Started with {self.interval_hours}h interval")
    
    async def stop(self):
        """Stop the scheduler loop"""
        if not self._running:
            return
        
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        
        logger.info("[ARIE Scheduler] Stopped")
    
    async def _schedule_loop(self):
        """Main scheduling loop"""
        while self._running:
            try:
                # Publish tick event
                await self._publish_tick()
                
                # Run integrity scan
                summary = await self._run_scan()
                
                # Publish summary
                await self._publish_summary(summary)
                
                # Log results
                self._log_run(summary)
                
                # Wait for next interval
                await asyncio.sleep(self.interval_hours * 3600)
                
            except asyncio.CancelledError:
                logger.info("[ARIE Scheduler] Loop cancelled")
                break
            except Exception as e:
                logger.exception(f"[ARIE Scheduler] Error in schedule loop: {e}")
                # Continue running even on error, retry after interval
                await asyncio.sleep(self.interval_hours * 3600)
    
    async def _run_scan(self):
        """Execute ARIE scan with SAFE_EDIT policy"""
        from .models import PolicyType
        
        logger.info("[ARIE Scheduler] Running scheduled integrity scan")
        
        try:
            # Run scan with SAFE_EDIT policy
            summary = self.engine.run(
                policy=PolicyType.SAFE_EDIT,
                dry_run=False,
                apply=True
            )
            
            logger.info(f"[ARIE Scheduler] Scan complete: {summary.findings_count} findings, "
                       f"{summary.fixes_applied} fixes applied")
            
            return summary
            
        except Exception as e:
            logger.exception(f"[ARIE Scheduler] Scan failed: {e}")
            raise
    
    async def _publish_tick(self):
        """Publish schedule tick event to Genesis"""
        if not self.bus:
            return
        
        await self.bus.publish("arie.schedule.tick", {
            "timestamp": datetime.now(UTC).isoformat() + "Z",
            "interval_hours": self.interval_hours
        })
    
    async def _publish_summary(self, summary):
        """Publish schedule summary to Genesis"""
        if not self.bus:
            return
        
        await self.bus.publish("arie.schedule.summary", {
            "run_id": summary.run_id,
            "timestamp": summary.timestamp,
            "findings_count": summary.findings_count,
            "fixes_applied": summary.fixes_applied,
            "fixes_failed": summary.fixes_failed,
            "certification_status": summary.certification_status,
            "duration_seconds": summary.duration_seconds
        })
    
    def _log_run(self, summary):
        """Log run results to JSON files"""
        timestamp = datetime.now(UTC).isoformat().replace("+00:00", "Z")
        
        # Create autorun log entry
        autorun_entry = {
            "timestamp": timestamp,
            "run_id": summary.run_id,
            "findings_count": summary.findings_count,
            "fixes_applied": summary.fixes_applied,
            "fixes_failed": summary.fixes_failed,
            "duration_seconds": summary.duration_seconds
        }
        
        # Append to autorun log
        autorun_log = self.logs_dir / "arie_autorun.json"
        self._append_json_log(autorun_log, autorun_entry)
        
        # Log certified patches
        if summary.patches:
            for patch in summary.patches:
                certified_entry = {
                    "timestamp": timestamp,
                    "patch_id": patch.id,
                    "certified": patch.certified,
                    "certificate_id": patch.certificate_id,
                    "files_modified": patch.files_modified
                }
                certified_log = self.logs_dir / "arie_certified.json"
                self._append_json_log(certified_log, certified_entry)
    
    def _append_json_log(self, log_path: Path, entry: dict):
        """Append entry to JSON log file"""
        try:
            # Read existing log
            if log_path.exists():
                with open(log_path, 'r') as f:
                    log_data = json.load(f)
            else:
                log_data = []
            
            # Append new entry
            log_data.append(entry)
            
            # Keep only last 100 entries
            log_data = log_data[-100:]
            
            # Write back
            with open(log_path, 'w') as f:
                json.dump(log_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"[ARIE Scheduler] Failed to write log {log_path}: {e}")
    
    async def trigger_manual_run(self, requester: str = "unknown") -> dict:
        """
        Manually trigger a scheduled run (Admiral only)
        
        Args:
            requester: User handle requesting the run
            
        Returns:
            Run summary dict
        """
        if self.admiral_only_apply:
            # Check if requester is Admiral
            owner_handle = os.getenv("STEWARD_OWNER_HANDLE", "")
            if requester != owner_handle:
                raise PermissionError(f"Only Admiral ({owner_handle}) can trigger manual ARIE runs")
        
        logger.info(f"[ARIE Scheduler] Manual run triggered by {requester}")
        
        summary = await self._run_scan()
        await self._publish_summary(summary)
        self._log_run(summary)
        
        return {
            "run_id": summary.run_id,
            "findings_count": summary.findings_count,
            "fixes_applied": summary.fixes_applied,
            "fixes_failed": summary.fixes_failed,
            "duration_seconds": summary.duration_seconds
        }
