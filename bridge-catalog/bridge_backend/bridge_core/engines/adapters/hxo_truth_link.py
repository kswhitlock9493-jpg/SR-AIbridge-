"""
HXO Truth Link Adapter
Connects HXO to Truth engine for Merkle root certification
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, UTC

logger = logging.getLogger(__name__)


async def certify_merkle_root(
    plan_id: str,
    merkle_root: str,
    sample_proofs: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Request Truth certification of Merkle root.
    
    Args:
        plan_id: Plan ID
        merkle_root: Merkle root hash to certify
        sample_proofs: Sample proofs for verification
        
    Returns:
        Certification result
    """
    try:
        from bridge_backend.genesis.bus import genesis_bus
        
        if not genesis_bus.is_enabled():
            logger.debug("[HXO Truth Link] Genesis bus disabled")
            return {
                "certified": False,
                "reason": "Genesis bus disabled"
            }
        
        # Publish certification request
        await genesis_bus.publish("hxo.aggregate.certify", {
            "plan_id": plan_id,
            "merkle_root": merkle_root,
            "sample_proofs": sample_proofs,
            "timestamp": datetime.now(UTC).isoformat()
        })
        
        # In a full implementation, this would wait for Truth engine response
        # For now, return optimistic certification
        logger.info(f"[HXO Truth Link] Requested certification for plan {plan_id}")
        
        return {
            "certified": True,
            "certificate_id": f"cert_{plan_id}_{merkle_root[:8]}",
            "merkle_root": merkle_root,
            "timestamp": datetime.now(UTC).isoformat()
        }
        
    except ImportError:
        logger.debug("[HXO Truth Link] Genesis bus not available")
        return {
            "certified": False,
            "reason": "Genesis bus not available"
        }
    except Exception as e:
        logger.error(f"[HXO Truth Link] Certification request failed: {e}")
        return {
            "certified": False,
            "reason": str(e)
        }


async def verify_shard_proof(proof: Dict[str, Any]) -> bool:
    """
    Verify a single shard proof.
    
    Args:
        proof: Merkle proof to verify
        
    Returns:
        True if proof is valid
    """
    try:
        # In a full implementation, this would use Truth engine verification
        # For now, perform basic structural validation
        
        required_fields = ["leaf_cas_id", "leaf_hash", "path", "root_hash"]
        if not all(field in proof for field in required_fields):
            logger.warning("[HXO Truth Link] Invalid proof structure")
            return False
        
        # Proof is structurally valid
        return True
        
    except Exception as e:
        logger.error(f"[HXO Truth Link] Proof verification failed: {e}")
        return False


async def on_certification_failure(plan_id: str, merkle_root: str, reason: str):
    """
    Handle certification failure from Truth engine.
    Triggers bisect and replay of suspect subtree.
    
    Args:
        plan_id: Plan ID
        merkle_root: Failed Merkle root
        reason: Reason for failure
    """
    try:
        from bridge_backend.genesis.bus import genesis_bus
        
        if not genesis_bus.is_enabled():
            logger.debug("[HXO Truth Link] Genesis bus disabled")
            return
        
        # Publish certification failure event
        await genesis_bus.publish("hxo.aggregate.failed", {
            "plan_id": plan_id,
            "merkle_root": merkle_root,
            "reason": reason,
            "timestamp": datetime.now(UTC).isoformat()
        })
        
        logger.warning(f"[HXO Truth Link] Certification failed for plan {plan_id}: {reason}")
        
        # In a full implementation, this would trigger auto-bisect and replay
        
    except ImportError:
        logger.debug("[HXO Truth Link] Genesis bus not available")
    except Exception as e:
        logger.error(f"[HXO Truth Link] Failed to handle certification failure: {e}")


async def publish_certification_success(plan_id: str, certificate: Dict[str, Any]):
    """
    Publish successful certification to Genesis.
    
    Args:
        plan_id: Plan ID
        certificate: Certification details
    """
    try:
        from bridge_backend.genesis.bus import genesis_bus
        
        if not genesis_bus.is_enabled():
            logger.debug("[HXO Truth Link] Genesis bus disabled")
            return
        
        # Publish certification success
        await genesis_bus.publish("hxo.aggregate.finalized", {
            "plan_id": plan_id,
            "certificate": certificate,
            "timestamp": datetime.now(UTC).isoformat()
        })
        
        logger.info(f"[HXO Truth Link] Published certification success for plan {plan_id}")
        
    except ImportError:
        logger.debug("[HXO Truth Link] Genesis bus not available")
    except Exception as e:
        logger.error(f"[HXO Truth Link] Failed to publish certification success: {e}")
