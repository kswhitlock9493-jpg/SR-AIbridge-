"""
Umbra Truth Link Adapter
Connects Umbra Lattice to Truth Engine for certification
"""

import logging
from typing import Dict, Any
from datetime import datetime, UTC

logger = logging.getLogger(__name__)


async def certify_lattice_record(record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Request Truth certification for Lattice record
    
    Args:
        record: Lattice record (nodes/edges)
        
    Returns:
        Certification result
    """
    try:
        from bridge_backend.bridge_core.engines.truth.service import TruthEngine
        
        truth_engine = TruthEngine()
        
        # Create certification request
        cert_request = {
            "context": "umbra_lattice_record",
            "record_type": record.get("type", "unknown"),
            "node_count": len(record.get("nodes", [])),
            "edge_count": len(record.get("edges", [])),
            "timestamp": datetime.now(UTC).isoformat()
        }
        
        # Request certification
        result = await truth_engine.certify(cert_request)
        
        if result.get("certified"):
            logger.info(f"[Umbra Truth Link] Record certified: {result.get('certificate_id')}")
        else:
            logger.warning(f"[Umbra Truth Link] Record not certified: {result.get('reason')}")
        
        return result
        
    except ImportError:
        logger.debug("[Umbra Truth Link] Truth engine not available")
        return {"certified": False, "reason": "truth_engine_unavailable"}
    except Exception as e:
        logger.error(f"[Umbra Truth Link] Certification failed: {e}")
        return {"certified": False, "reason": str(e)}


async def on_certification_failure(record_id: str, reason: str):
    """
    Handle certification failure
    
    Args:
        record_id: Record ID that failed certification
        reason: Failure reason
    """
    try:
        from bridge_backend.genesis.bus import genesis_bus
        
        if not genesis_bus.is_enabled():
            logger.debug("[Umbra Truth Link] Genesis bus disabled")
            return
        
        # Publish certification failure event
        await genesis_bus.publish("umbra.lattice.cert_failed", {
            "record_id": record_id,
            "reason": reason,
            "timestamp": datetime.now(UTC).isoformat()
        })
        
        logger.warning(f"[Umbra Truth Link] Certification failed for {record_id}: {reason}")
        
    except ImportError:
        logger.debug("[Umbra Truth Link] Genesis bus not available")
    except Exception as e:
        logger.error(f"[Umbra Truth Link] Failed to handle certification failure: {e}")


async def publish_certification_success(record_id: str, certificate: Dict[str, Any]):
    """
    Publish certification success event
    
    Args:
        record_id: Certified record ID
        certificate: Certificate data
    """
    try:
        from bridge_backend.genesis.bus import genesis_bus
        
        if not genesis_bus.is_enabled():
            logger.debug("[Umbra Truth Link] Genesis bus disabled")
            return
        
        # Publish success event
        await genesis_bus.publish("umbra.lattice.certified", {
            "record_id": record_id,
            "certificate_id": certificate.get("certificate_id"),
            "timestamp": datetime.now(UTC).isoformat()
        })
        
        logger.info(f"[Umbra Truth Link] Published certification success for {record_id}")
        
    except ImportError:
        logger.debug("[Umbra Truth Link] Genesis bus not available")
    except Exception as e:
        logger.error(f"[Umbra Truth Link] Failed to publish certification success: {e}")
