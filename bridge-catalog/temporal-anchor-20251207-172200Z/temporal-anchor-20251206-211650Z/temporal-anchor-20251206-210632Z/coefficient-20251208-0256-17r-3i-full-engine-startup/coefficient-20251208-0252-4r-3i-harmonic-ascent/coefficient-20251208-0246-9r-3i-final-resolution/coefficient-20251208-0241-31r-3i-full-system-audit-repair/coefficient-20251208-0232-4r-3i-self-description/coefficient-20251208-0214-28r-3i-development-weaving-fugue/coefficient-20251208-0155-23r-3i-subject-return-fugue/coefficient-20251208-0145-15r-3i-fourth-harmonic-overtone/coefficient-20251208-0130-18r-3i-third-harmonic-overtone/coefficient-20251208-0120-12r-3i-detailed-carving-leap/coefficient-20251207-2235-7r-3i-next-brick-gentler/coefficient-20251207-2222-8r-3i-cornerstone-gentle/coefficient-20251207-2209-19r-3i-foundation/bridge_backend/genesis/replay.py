"""
Genesis Event Replay
Time-travel and event replay with watermark support
"""
import logging
from typing import Optional, Callable, Dict, Any, List
from datetime import datetime
from .persistence import genesis_persistence
from .bus import genesis_bus

logger = logging.getLogger(__name__)


class GenesisReplay:
    """
    Event replay system for time-travel and recovery
    
    Features:
    - Replay events from watermark
    - Topic filtering for selective replay
    - Async event re-emission
    """
    
    def __init__(self):
        self._persistence = genesis_persistence
    
    async def replay_from_watermark(
        self,
        watermark: int,
        topic_pattern: Optional[str] = None,
        limit: int = 1000,
        emit: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Replay events from a specific watermark
        
        Args:
            watermark: Starting watermark (inclusive)
            topic_pattern: Optional SQL LIKE pattern (e.g. "engine.truth%")
            limit: Maximum events to replay
            emit: If True, re-emit events to bus; if False, just return them
        
        Returns:
            List of replayed events
        """
        logger.info(f"🔄 Replaying events from watermark {watermark} (topic={topic_pattern}, limit={limit})")
        
        # Fetch events
        events = await self._persistence.get_events(
            topic_pattern=topic_pattern,
            from_watermark=watermark,
            limit=limit
        )
        
        if not events:
            logger.info("📭 No events to replay")
            return []
        
        logger.info(f"📦 Found {len(events)} events to replay")
        
        # Re-emit events if requested
        if emit:
            for event in events:
                try:
                    await genesis_bus.publish(event["topic"], event)
                    logger.debug(f"✅ Replayed event {event['id']} (watermark {event['watermark']})")
                except Exception as e:
                    logger.error(f"❌ Failed to replay event {event['id']}: {e}")
        
        return events
    
    async def replay_from_timestamp(
        self,
        from_ts: datetime,
        topic_pattern: Optional[str] = None,
        limit: int = 1000,
        emit: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Replay events from a specific timestamp
        
        Note: This is less efficient than watermark-based replay.
        For production, prefer replay_from_watermark.
        
        Args:
            from_ts: Starting timestamp (inclusive)
            topic_pattern: Optional SQL LIKE pattern
            limit: Maximum events to replay
            emit: If True, re-emit events to bus
        
        Returns:
            List of replayed events
        """
        # Fetch all matching events and filter by timestamp
        # This is a simple implementation; for production, add timestamp index
        events = await self._persistence.get_events(
            topic_pattern=topic_pattern,
            limit=limit
        )
        
        # Filter by timestamp
        filtered = [
            e for e in events
            if datetime.fromisoformat(e["ts"].replace("Z", "+00:00")) >= from_ts
        ]
        
        if not filtered:
            logger.info("📭 No events to replay in time range")
            return []
        
        logger.info(f"📦 Found {len(filtered)} events to replay from {from_ts}")
        
        # Re-emit if requested
        if emit:
            for event in filtered:
                try:
                    await genesis_bus.publish(event["topic"], event)
                    logger.debug(f"✅ Replayed event {event['id']}")
                except Exception as e:
                    logger.error(f"❌ Failed to replay event {event['id']}: {e}")
        
        return filtered
    
    async def get_current_watermark(self) -> int:
        """Get current event watermark"""
        return await self._persistence.get_watermark()


# Global replay instance
genesis_replay = GenesisReplay()


# CLI helper for manual replay
async def replay_cli(from_watermark: Optional[int] = None, from_ts: Optional[str] = None, topic: str = "%"):
    """
    CLI helper for replaying events
    
    Usage:
        python -m bridge_backend.genesis.replay --from-watermark 100
        python -m bridge_backend.genesis.replay --from-ts "2025-10-10T00:00:00Z" --topic "engine.truth%"
    """
    replay = GenesisReplay()
    
    if from_watermark is not None:
        events = await replay.replay_from_watermark(from_watermark, topic_pattern=topic)
    elif from_ts:
        ts = datetime.fromisoformat(from_ts.replace("Z", "+00:00"))
        events = await replay.replay_from_timestamp(ts, topic_pattern=topic)
    else:
        print("Error: Must specify --from-watermark or --from-ts")
        return
    
    print(f"✅ Replayed {len(events)} events")
    for event in events[:10]:  # Show first 10
        print(f"  - {event['watermark']}: {event['topic']} ({event['id']})")
    if len(events) > 10:
        print(f"  ... and {len(events) - 10} more")


if __name__ == "__main__":
    import sys
    import asyncio
    
    # Simple CLI argument parsing
    args = sys.argv[1:]
    kwargs = {}
    
    i = 0
    while i < len(args):
        if args[i] == "--from-watermark" and i + 1 < len(args):
            kwargs["from_watermark"] = int(args[i + 1])
            i += 2
        elif args[i] == "--from-ts" and i + 1 < len(args):
            kwargs["from_ts"] = args[i + 1]
            i += 2
        elif args[i] == "--topic" and i + 1 < len(args):
            kwargs["topic"] = args[i + 1]
            i += 2
        else:
            i += 1
    
    asyncio.run(replay_cli(**kwargs))
