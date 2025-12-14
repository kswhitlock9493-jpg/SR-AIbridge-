"""
Background Task Queue for TDE-X
Persistent async queue for long-running tasks that continue after deploy
"""
import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)

QUEUE_DIR = Path("bridge_backend/.queue")
QUEUE_DIR.mkdir(parents=True, exist_ok=True)


class BgQueue:
    """Background task queue with persistence"""
    
    def __init__(self):
        self.loop = asyncio.get_event_loop()
    
    def enqueue(self, job_name: str, payload: Dict[str, Any]):
        """
        Add a job to the queue
        
        Args:
            job_name: Job identifier
            payload: Job parameters
        """
        try:
            f = QUEUE_DIR / f"{job_name}.json"
            f.write_text(json.dumps(payload, indent=2))
            logger.info(f"[BgQueue] Enqueued: {job_name}")
        except Exception as e:
            logger.error(f"[BgQueue] Failed to enqueue {job_name}: {e}")
    
    async def drain(self):
        """Process all queued jobs"""
        logger.info("[BgQueue] Starting drain...")
        
        for f in QUEUE_DIR.glob("*.json"):
            try:
                payload = json.loads(f.read_text())
                await self._run_job(f.stem, payload)
                f.unlink(missing_ok=True)
                logger.info(f"[BgQueue] Completed: {f.stem}")
            except Exception as e:
                logger.error(f"[BgQueue] Failed to process {f.stem}: {e}")
                # non-fatal: ticket logged by StabilizationDomain from caller
    
    async def _run_job(self, job_name: str, payload: Dict[str, Any]):
        """
        Execute a background job
        
        Args:
            job_name: Job identifier
            payload: Job parameters
        """
        # Register your background tasks here
        if job_name == "upload_assets":
            from .shards.diagnostics import upload_assets
            await upload_assets(**payload)
        elif job_name == "emit_metrics":
            from .shards.diagnostics import emit_metrics
            await emit_metrics(**payload)
        else:
            logger.warning(f"[BgQueue] Unknown job type: {job_name}")
    
    def get_depth(self) -> int:
        """Get current queue depth"""
        return len(list(QUEUE_DIR.glob("*.json")))


# Global singleton queue instance
queue = BgQueue()
