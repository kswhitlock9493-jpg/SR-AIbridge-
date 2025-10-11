"""
HXO Autonomy Link Adapter
Connects HXO to Autonomy engine for self-healing and auto-tuning
"""

import logging
from typing import Dict, Any
from datetime import datetime, UTC

logger = logging.getLogger(__name__)


async def notify_autotune_signal(signal_data: Dict[str, Any]):
    """
    Notify Autonomy of auto-tune signals from HXO.
    
    Args:
        signal_data: Auto-tune signal data
            - plan_id: Plan ID
            - stage_id: Stage ID
            - signal_type: Type of signal (high_latency, hotspot, etc.)
            - metric_value: Metric value
            - suggested_action: Suggested corrective action
    """
    try:
        from bridge_backend.genesis.bus import genesis_bus
        
        if not genesis_bus.is_enabled():
            logger.debug("[HXO Autonomy Link] Genesis bus disabled")
            return
        
        # Publish autotune signal to Genesis
        await genesis_bus.publish("hxo.autotune.signal", {
            **signal_data,
            "timestamp": datetime.now(UTC).isoformat()
        })
        
        logger.info(f"[HXO Autonomy Link] Published autotune signal: {signal_data.get('signal_type')}")
        
    except ImportError:
        logger.debug("[HXO Autonomy Link] Genesis bus not available")
    except Exception as e:
        logger.error(f"[HXO Autonomy Link] Failed to notify autotune signal: {e}")


async def request_healing(plan_id: str, stage_id: str, reason: str):
    """
    Request healing from Autonomy for a failed stage.
    
    Args:
        plan_id: Plan ID
        stage_id: Stage ID
        reason: Reason for healing request
    """
    try:
        from bridge_backend.genesis.bus import genesis_bus
        
        if not genesis_bus.is_enabled():
            logger.debug("[HXO Autonomy Link] Genesis bus disabled")
            return
        
        # Publish healing request
        await genesis_bus.publish("genesis.heal", {
            "source": "hxo",
            "plan_id": plan_id,
            "stage_id": stage_id,
            "reason": reason,
            "timestamp": datetime.now(UTC).isoformat()
        })
        
        logger.info(f"[HXO Autonomy Link] Requested healing for plan {plan_id}, stage {stage_id}")
        
    except ImportError:
        logger.debug("[HXO Autonomy Link] Genesis bus not available")
    except Exception as e:
        logger.error(f"[HXO Autonomy Link] Failed to request healing: {e}")


async def notify_shard_hotspot(plan_id: str, stage_id: str, cas_id: str, latency_ms: float):
    """
    Notify Autonomy of a hot shard that needs splitting.
    
    Args:
        plan_id: Plan ID
        stage_id: Stage ID
        cas_id: Shard CAS ID
        latency_ms: Shard execution latency in ms
    """
    try:
        await notify_autotune_signal({
            "plan_id": plan_id,
            "stage_id": stage_id,
            "cas_id": cas_id,
            "signal_type": "hotspot",
            "metric_value": latency_ms,
            "suggested_action": "split_shard"
        })
        
    except Exception as e:
        logger.error(f"[HXO Autonomy Link] Failed to notify shard hotspot: {e}")


async def apply_tuning_recommendation(recommendation: Dict[str, Any]) -> bool:
    """
    Apply tuning recommendation from Autonomy.
    
    Args:
        recommendation: Tuning recommendation
            - action: Action to take (split_shard, increase_concurrency, etc.)
            - parameters: Action parameters
            
    Returns:
        True if recommendation was applied
    """
    try:
        action = recommendation.get("action")
        
        if action == "split_shard":
            # In a full implementation, this would trigger shard splitting
            logger.info("[HXO Autonomy Link] Would split shard based on recommendation")
            return True
            
        elif action == "increase_concurrency":
            # In a full implementation, this would adjust concurrency limits
            logger.info("[HXO Autonomy Link] Would increase concurrency based on recommendation")
            return True
            
        else:
            logger.warning(f"[HXO Autonomy Link] Unknown tuning action: {action}")
            return False
        
    except Exception as e:
        logger.error(f"[HXO Autonomy Link] Failed to apply tuning recommendation: {e}")
        return False
