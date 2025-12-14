"""
Umbra Triage Mesh - Parity Link Adapter
Integrates with Parity Engine for environment convergence checks
"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


async def check_parity_for_heal(parity_checks: List[str]) -> Dict[str, Any]:
    """
    Run parity checks before heal execution
    
    Args:
        parity_checks: List of parity check identifiers (e.g., "env:netlify/render")
        
    Returns:
        Parity check results
    """
    try:
        from bridge_backend.engines.envrecon.parity import check_parity as parity_check
        
        results = []
        all_passed = True
        
        for check_spec in parity_checks:
            try:
                # Parse check spec (e.g., "env:netlify/render")
                if check_spec.startswith("env:"):
                    platforms = check_spec[4:].split("/")
                    
                    # Run parity check between platforms
                    result = await parity_check(platforms)
                    results.append({
                        "check": check_spec,
                        "passed": result.get("ok", False),
                        "details": result
                    })
                    
                    if not result.get("ok", False):
                        all_passed = False
                        logger.warning(f"[Umbra Parity Link] Parity check failed: {check_spec}")
                
                else:
                    logger.warning(f"[Umbra Parity Link] Unknown check spec format: {check_spec}")
                    results.append({
                        "check": check_spec,
                        "passed": False,
                        "error": "unknown_format"
                    })
                    all_passed = False
            
            except Exception as e:
                logger.error(f"[Umbra Parity Link] Check failed for {check_spec}: {e}")
                results.append({
                    "check": check_spec,
                    "passed": False,
                    "error": str(e)
                })
                all_passed = False
        
        return {
            "ok": all_passed,
            "total_checks": len(parity_checks),
            "passed_checks": sum(1 for r in results if r.get("passed", False)),
            "results": results
        }
    
    except ImportError:
        logger.warning("[Umbra Parity Link] Parity engine not available")
        return {
            "ok": True,  # Don't block healing if parity engine unavailable
            "reason": "parity_engine_unavailable"
        }
    except Exception as e:
        logger.error(f"[Umbra Parity Link] Parity check error: {e}")
        return {
            "ok": False,
            "error": str(e)
        }


async def verify_parity_after_heal(parity_checks: List[str]) -> Dict[str, Any]:
    """
    Verify parity after heal execution to ensure convergence
    
    Args:
        parity_checks: List of parity check identifiers
        
    Returns:
        Verification results
    """
    # Use same logic as pre-checks
    result = await check_parity_for_heal(parity_checks)
    
    if result.get("ok"):
        logger.info("[Umbra Parity Link] Post-heal parity verification passed")
    else:
        logger.warning("[Umbra Parity Link] Post-heal parity verification failed")
    
    return result


async def emit_parity_event(event_type: str, data: Dict[str, Any]):
    """
    Emit parity event to Genesis bus
    
    Args:
        event_type: Event type (precheck, postcheck, failed, etc.)
        data: Event data
    """
    try:
        from bridge_backend.genesis.bus import genesis_bus
        
        if not genesis_bus.is_enabled():
            return
        
        await genesis_bus.publish(f"triage.parity.{event_type}", {
            **data,
            "source": "umbra_triage"
        })
        
        logger.debug(f"[Umbra Parity Link] Emitted event: triage.parity.{event_type}")
    
    except Exception as e:
        logger.warning(f"[Umbra Parity Link] Failed to emit event: {e}")
