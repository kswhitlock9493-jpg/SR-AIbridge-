"""
Unified Bridge Event Bus
Debounced, asyncio-safe PubSub for engine-wide events
"""

from typing import Callable, Dict, Any, DefaultDict, List
from collections import defaultdict
import asyncio
import logging

logger = logging.getLogger(__name__)


class BridgeEventBus:
    """
    Unified event bus for all bridge engines
    Supports Truth/Parser hooks and Cascade validators
    """
    
    def __init__(self):
        self._subs: DefaultDict[str, List[Callable[[Dict[str, Any]], None]]] = defaultdict(list)
        self._lock = asyncio.Lock()
        self._truth_validator = None
        self._parser_normalizer = None
        self._cascade_pre = []
        self._cascade_post = []
        logger.info("🌉 BridgeEventBus initialized")

    def set_truth_validator(self, fn: Callable[[Dict[str,Any]], Dict[str,Any]]):
        """Set Truth Engine validator hook"""
        self._truth_validator = fn
        logger.info("✅ Truth validator registered")
    
    def set_parser_normalizer(self, fn: Callable[[Dict[str,Any]], Dict[str,Any]]):
        """Set Parser Engine normalizer hook"""
        self._parser_normalizer = fn
        logger.info("✅ Parser normalizer registered")
    
    def add_cascade_pre(self, fn):
        """Add Cascade pre-hook"""
        self._cascade_pre.append(fn)
        logger.info("✅ Cascade pre-hook registered")
    
    def add_cascade_post(self, fn):
        """Add Cascade post-hook"""
        self._cascade_post.append(fn)
        logger.info("✅ Cascade post-hook registered")

    async def publish(self, topic: str, event: Dict[str, Any]):
        """
        Publish event to topic with hooks applied
        
        Args:
            topic: Event topic name
            event: Event payload dictionary
        """
        async with self._lock:
            e = dict(event)
            
            # Apply cascade pre-hooks
            for fn in self._cascade_pre:
                e = await fn(e) if asyncio.iscoroutinefunction(fn) else fn(e)
            
            # Apply parser normalizer
            if self._parser_normalizer:
                e = await self._parser_normalizer(e) if asyncio.iscoroutinefunction(self._parser_normalizer) else self._parser_normalizer(e)
            
            # Apply truth validator
            if self._truth_validator:
                e = await self._truth_validator(e) if asyncio.iscoroutinefunction(self._truth_validator) else self._truth_validator(e)
            
            # Apply cascade post-hooks
            for fn in self._cascade_post:
                e = await fn(e) if asyncio.iscoroutinefunction(fn) else fn(e)
            
            # Fan out to subscribers
            for sub in self._subs.get(topic, []):
                try:
                    out = sub(e)
                    if asyncio.iscoroutine(out):
                        await out
                except Exception as ex:
                    logger.error(f"❌ Subscriber error on topic {topic}: {ex}")

    def subscribe(self, topic: str, handler: Callable[[Dict[str,Any]], Any]):
        """
        Subscribe to a topic
        
        Args:
            topic: Topic name
            handler: Callback function (sync or async)
        """
        self._subs[topic].append(handler)
        logger.info(f"📡 Subscribed to topic: {topic}")


# Global singleton bus instance
bus = BridgeEventBus()
