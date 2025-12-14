"""
HXO Federation Link Adapter
Provides queue mechanisms for shard claims and execution
"""

import logging
from typing import Dict, Any, Optional
import asyncio

logger = logging.getLogger(__name__)


class HXOFederationLink:
    """
    Federation link for HXO.
    Provides local and deferred queues for shard execution.
    """
    
    def __init__(self):
        self.local_queue: asyncio.Queue = asyncio.Queue()
        self.deferred_queue_enabled = False
        
        # Try to import federation client
        try:
            from bridge_backend.bridge_core.federation_client import FederationClient
            self.federation_available = True
            logger.info("[HXO Federation Link] Federation client available")
        except ImportError:
            self.federation_available = False
            logger.info("[HXO Federation Link] Federation client not available, using local queue only")
    
    async def enqueue_shard(self, shard_data: Dict[str, Any], priority: str = "normal"):
        """
        Enqueue a shard for execution.
        
        Args:
            shard_data: Shard specification and inputs
            priority: Execution priority (normal, high, critical)
        """
        try:
            # For now, use local queue
            await self.local_queue.put({
                "shard": shard_data,
                "priority": priority
            })
            
            logger.debug(f"[HXO Federation Link] Enqueued shard {shard_data.get('cas_id')}")
            
        except Exception as e:
            logger.error(f"[HXO Federation Link] Failed to enqueue shard: {e}")
    
    async def dequeue_shard(self, timeout: Optional[float] = None) -> Optional[Dict[str, Any]]:
        """
        Dequeue a shard for execution.
        
        Args:
            timeout: Timeout in seconds
            
        Returns:
            Shard data or None if queue is empty
        """
        try:
            if timeout:
                item = await asyncio.wait_for(self.local_queue.get(), timeout=timeout)
            else:
                item = await self.local_queue.get()
            
            return item.get("shard")
            
        except asyncio.TimeoutError:
            return None
        except Exception as e:
            logger.error(f"[HXO Federation Link] Failed to dequeue shard: {e}")
            return None
    
    async def get_queue_depth(self) -> int:
        """Get current queue depth"""
        return self.local_queue.qsize()
    
    async def announce_plan(self, plan_data: Dict[str, Any]):
        """
        Announce plan execution to federation network.
        
        Args:
            plan_data: Plan metadata
        """
        if not self.federation_available:
            return
        
        try:
            # In a full implementation, this would broadcast to federation network
            logger.info(f"[HXO Federation Link] Would announce plan {plan_data.get('plan_id')} to federation")
            
        except Exception as e:
            logger.error(f"[HXO Federation Link] Failed to announce plan: {e}")


# Global singleton
_hxo_federation_link: Optional[HXOFederationLink] = None


def get_hxo_federation_link() -> HXOFederationLink:
    """Get or create global HXO federation link"""
    global _hxo_federation_link
    if _hxo_federation_link is None:
        _hxo_federation_link = HXOFederationLink()
    return _hxo_federation_link
