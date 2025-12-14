"""
Federation Hooks for TDE-X
Event-driven announcements to Deploy Federation Bus
"""
import logging
from typing import Dict, Any
from .stabilization import StabilizationDomain

logger = logging.getLogger(__name__)


async def announce(stage: str, payload: Dict[str, Any]):
    """
    Announce deployment stage completion to federation bus
    
    Args:
        stage: Stage name (e.g., "bootstrap", "runtime", "diagnostics")
        payload: Stage outcome data
    """
    with StabilizationDomain(f"federation:{stage}"):
        try:
            from bridge_backend.bridge_core.heritage.event_bus import bus
            await bus.publish("deploy.events", {"stage": stage, **payload})
            logger.info(f"[Federation] Announced: {stage}")
        except ImportError:
            logger.warning(f"[Federation] Event bus not available for {stage}")
        except Exception as e:
            logger.error(f"[Federation] Failed to announce {stage}: {e}")
            raise  # Let StabilizationDomain handle it
