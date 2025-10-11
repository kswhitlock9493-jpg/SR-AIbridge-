"""
Deploy Parity Endpoint
Returns current shard states + background queue status
"""
from fastapi import APIRouter
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/diagnostics", tags=["diagnostics"])


@router.get("/deploy-parity")
def get_deploy_parity():
    """
    Get deployment parity state
    Returns shard states + background queue status (compact JSON)
    """
    try:
        from bridge_backend.runtime.tde_x.queue import queue
        from pathlib import Path
        
        # Get queue status
        queue_depth = queue.get_depth()
        
        # Check for shard completion markers (simplified)
        # In production, this would track actual shard outcomes
        shards_complete = {
            "bootstrap": True,  # If we're serving this endpoint, bootstrap succeeded
            "runtime": True,    # Same for runtime
            "diagnostics": queue_depth == 0  # Diagnostics complete when queue is empty
        }
        
        # Get ticket count
        ticket_dir = Path("bridge_backend/diagnostics/stabilization_tickets")
        ticket_count = len(list(ticket_dir.glob("*.md"))) if ticket_dir.exists() else 0
        
        return {
            "status": "ok",
            "version": "1.9.7a",
            "shards": shards_complete,
            "queue": {
                "depth": queue_depth,
                "active": queue_depth > 0
            },
            "tickets": {
                "count": ticket_count,
                "has_issues": ticket_count > 0
            }
        }
    except Exception as e:
        logger.error(f"[Deploy Parity] Error: {e}")
        return {
            "status": "error",
            "error": str(e),
            "version": "1.9.7a"
        }
