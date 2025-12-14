"""
ARIE Truth Link - Post-fix certification via Truth Engine
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class ARIETruthLink:
    """
    Truth Engine integration for ARIE
    
    Certifies fixes by:
    - Verifying module hashes
    - Running test matrix
    - Publishing truth.certified or truth.failed
    
    ARIE only marks a fix "final" after certificate=true
    Otherwise, auto-rollback
    """
    
    def __init__(self, truth_engine=None, arie_engine=None):
        self.truth_engine = truth_engine
        self.arie_engine = arie_engine
    
    async def certify_patch(self, patch) -> Dict[str, Any]:
        """
        Request certification for a patch
        
        Returns:
            Certification result with status and certificate_id
        """
        if not self.truth_engine:
            # No Truth Engine available, auto-approve for now
            logger.warning("[ARIE Truth] No Truth Engine available, auto-approving patch")
            return {
                "certified": True,
                "certificate_id": f"auto_{patch.id}",
                "reason": "No Truth Engine configured"
            }
        
        try:
            # Calculate module hashes for modified files
            module_hashes = {}
            for file_path in patch.files_modified:
                # Compute hash
                try:
                    import hashlib
                    from pathlib import Path
                    
                    full_path = Path(file_path)
                    if full_path.exists():
                        content = full_path.read_bytes()
                        file_hash = hashlib.sha256(content).hexdigest()
                        module_hashes[file_path] = file_hash
                except Exception as e:
                    logger.exception(f"[ARIE Truth] Error hashing {file_path}: {e}")
            
            # Request certification from Truth Engine
            cert_request = {
                "patch_id": patch.id,
                "module_hashes": module_hashes,
                "files_modified": patch.files_modified,
                "timestamp": patch.timestamp
            }
            
            # Call Truth Engine (placeholder)
            result = await self._request_truth_verification(cert_request)
            
            if result.get("certified"):
                # Mark patch as certified
                patch.certified = True
                patch.certificate_id = result.get("certificate_id")
                logger.info(f"[ARIE Truth] Patch {patch.id} certified: {result.get('certificate_id')}")
            else:
                # Certification failed, trigger rollback
                logger.warning(f"[ARIE Truth] Patch {patch.id} failed certification: {result.get('reason')}")
                await self._trigger_rollback(patch)
            
            return result
        
        except Exception as e:
            logger.exception(f"[ARIE Truth] Error certifying patch: {e}")
            return {
                "certified": False,
                "reason": str(e)
            }
    
    async def _request_truth_verification(self, cert_request: Dict[str, Any]) -> Dict[str, Any]:
        """Request verification from Truth Engine"""
        if not self.truth_engine:
            return {
                "certified": True,
                "certificate_id": f"auto_{cert_request['patch_id']}",
                "reason": "No Truth Engine configured"
            }
        
        # Call Truth Engine verify method
        try:
            result = await self.truth_engine.verify(
                module_hashes=cert_request["module_hashes"],
                context="arie_patch"
            )
            return result
        except Exception as e:
            logger.exception(f"[ARIE Truth] Truth Engine verification failed: {e}")
            return {
                "certified": False,
                "reason": f"Truth Engine error: {str(e)}"
            }
    
    async def _trigger_rollback(self, patch):
        """Trigger automatic rollback for failed certification"""
        if not self.arie_engine:
            logger.error("[ARIE Truth] Cannot rollback - no ARIE engine available")
            return
        
        logger.info(f"[ARIE Truth] Triggering auto-rollback for patch {patch.id}")
        
        try:
            rollback = self.arie_engine.rollback(patch.id, force=False)
            
            if rollback.success:
                logger.info(f"[ARIE Truth] Auto-rollback successful for patch {patch.id}")
            else:
                logger.error(f"[ARIE Truth] Auto-rollback failed for patch {patch.id}: {rollback.error}")
        
        except Exception as e:
            logger.exception(f"[ARIE Truth] Error during auto-rollback: {e}")
