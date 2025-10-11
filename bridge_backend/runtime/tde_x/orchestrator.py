"""
TDE-X Orchestrator
Coordinates shards with parallel execution and federation hooks
"""
import asyncio
import logging
from .shards import bootstrap, runtime, diagnostics
from .federation import announce
from .queue import queue
from typing import List, Any

logger = logging.getLogger(__name__)


async def run_tde_x() -> List[Any]:
    """
    Run TDE-X orchestrator with parallel shard execution
    
    Returns:
        List of shard results (may include exceptions)
    """
    logger.info("[TDE-X] 🚀 Orchestrator starting...")
    
    # Run core shards in parallel; diagnostics only enqueues work
    bootstrap_task = asyncio.create_task(bootstrap.run())
    runtime_task = asyncio.create_task(runtime.run())
    diag_task = asyncio.create_task(diagnostics.run_background())
    
    # Gather results (return_exceptions=True keeps failures isolated)
    results = await asyncio.gather(
        bootstrap_task,
        runtime_task,
        diag_task,
        return_exceptions=True
    )
    
    logger.info(f"[TDE-X] Shards complete: {len(results)} results")
    
    # Federation announcements for successful shards
    for r in results:
        if isinstance(r, dict) and "stage" in r:
            try:
                await announce(r["stage"], r)
            except Exception as e:
                logger.error(f"[TDE-X] Federation announcement failed: {e}")
    
    # Start draining background queue AFTER app is up (non-blocking)
    try:
        asyncio.create_task(queue.drain())
        logger.info("[TDE-X] Background queue drain started")
    except Exception as e:
        logger.error(f"[TDE-X] Failed to start queue drain: {e}")
    
    logger.info("[TDE-X] 🎉 Orchestration complete")
    return results
