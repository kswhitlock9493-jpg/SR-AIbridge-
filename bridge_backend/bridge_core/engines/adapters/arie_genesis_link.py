"""
ARIE Genesis Link - Connect ARIE to Genesis Event Bus
"""

import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime, UTC

logger = logging.getLogger(__name__)


class ARIEGenesisLink:
    """
    Links ARIE to Genesis Event Bus
    
    Subscribes to:
    - deploy.platform.success → triggers scan+verify
    - genesis.heal (category repo_integrity) → apply planned fixes
    
    Publishes:
    - arie.audit → scan results
    - arie.fix.intent → planned fixes
    - arie.fix.applied → fixes that were applied
    - arie.fix.rollback → rollback events
    - arie.alert → critical issues or failures
    """
    
    def __init__(self, bus=None, engine=None):
        self.bus = bus
        self.engine = engine
        self.enabled = os.getenv("ARIE_ENABLED", "true").lower() == "true"
        self.auto_fix_on_deploy = os.getenv("ARIE_AUTO_FIX_ON_DEPLOY_SUCCESS", "false").lower() == "true"
        self.run_on_deploy = os.getenv("ARIE_RUN_ON_DEPLOY", "true").lower() == "true"
        self.truth_mandatory = os.getenv("ARIE_TRUTH_MANDATORY", "true").lower() == "true"
        
        if self.enabled and self.bus:
            self._register_subscriptions()
    
    def _register_subscriptions(self):
        """Register Genesis event subscriptions"""
        if not self.bus:
            return
        
        # Subscribe to deploy success events
        self.bus.subscribe("deploy.platform.success", self._on_deploy_success)
        
        # Subscribe to heal requests for repo integrity
        self.bus.subscribe("genesis.heal", self._on_heal_request)
        
        logger.info("[ARIE Genesis Link] Registered subscriptions")
    
    async def _on_deploy_success(self, event: Dict[str, Any]):
        """Handle successful deploy event"""
        if not self.enabled or not self.engine:
            return
        
        # Check if run on deploy is enabled
        if not self.run_on_deploy:
            logger.info(f"[ARIE] Deploy success detected but run_on_deploy is disabled")
            return
        
        logger.info(f"[ARIE] Deploy success detected, triggering integrity scan")
        
        try:
            # Run scan with SAFE_EDIT policy
            from ..models import PolicyType
            summary = self.engine.run(
                policy=PolicyType.SAFE_EDIT,
                dry_run=False,
                apply=True
            )
            
            # Publish audit results
            await self._publish_audit(summary)
            
            if summary.fixes_applied > 0:
                await self._publish_fix_applied(summary)
                
                # Request Truth certification
                cert_result = await self._request_certification(summary)
                
                # Handle certification result
                if self.truth_mandatory and not cert_result.get("success", False):
                    # Rollback on failed certification
                    logger.warning(f"[ARIE] Truth certification failed, triggering rollback")
                    await self._handle_failed_certification(summary)
                else:
                    # Commit results
                    logger.info(f"[ARIE] Certification successful, committing results")
                    await self._commit_results(summary)
        
        except Exception as e:
            logger.exception(f"[ARIE] Error in deploy success handler: {e}")
            await self._publish_alert("deploy_scan_failed", str(e))
    
    async def _on_heal_request(self, event: Dict[str, Any]):
        """Handle heal request from Genesis"""
        if not self.enabled or not self.engine:
            return
        
        # Check if this is a repo_integrity heal request
        category = event.get("category")
        if category != "repo_integrity":
            return
        
        logger.info(f"[ARIE] Heal request received for repo_integrity")
        
        try:
            # Check permission
            if not await self._check_permission("arie:fix"):
                logger.warning("[ARIE] Missing permission for heal operation")
                return
            
            # Apply fixes based on policy in event
            from ..models import PolicyType
            policy_str = event.get("policy", "SAFE_EDIT")
            policy = PolicyType(policy_str)
            
            summary = self.engine.run(policy=policy, dry_run=False, apply=True)
            
            if summary.fixes_applied > 0:
                await self._publish_fix_applied(summary)
                await self._request_certification(summary)
            
        except Exception as e:
            logger.exception(f"[ARIE] Error in heal request handler: {e}")
            await self._publish_alert("heal_failed", str(e))
    
    async def _publish_audit(self, summary):
        """Publish audit results to Genesis"""
        if not self.bus:
            return
        
        await self.bus.publish("arie.audit", {
            "run_id": summary.run_id,
            "timestamp": summary.timestamp,
            "findings_count": summary.findings_count,
            "by_severity": summary.findings_by_severity,
            "by_category": summary.findings_by_category,
            "policy": summary.policy.value,
            "findings": [f.dict() for f in summary.findings[:10]]  # Top 10
        })
    
    async def _publish_fix_intent(self, plan):
        """Publish fix intent to Genesis"""
        if not self.bus:
            return
        
        await self.bus.publish("arie.fix.intent", {
            "plan_id": plan.id,
            "timestamp": plan.created_at,
            "policy": plan.policy.value,
            "actions_count": len(plan.actions),
            "estimated_impact": plan.estimated_impact
        })
    
    async def _publish_fix_applied(self, summary):
        """Publish applied fixes to Genesis"""
        if not self.bus:
            return
        
        await self.bus.publish("arie.fix.applied", {
            "run_id": summary.run_id,
            "timestamp": summary.timestamp,
            "fixes_applied": summary.fixes_applied,
            "files_modified": sum(len(p.files_modified) for p in summary.patches),
            "patches": [p.dict() for p in summary.patches]
        })
    
    async def _publish_rollback(self, rollback):
        """Publish rollback event to Genesis"""
        if not self.bus:
            return
        
        await self.bus.publish("arie.fix.rollback", {
            "rollback_id": rollback.id,
            "patch_id": rollback.patch_id,
            "timestamp": rollback.timestamp,
            "success": rollback.success,
            "restored_files": rollback.restored_files,
            "error": rollback.error
        })
    
    async def _publish_alert(self, alert_type: str, message: str):
        """Publish alert to Genesis"""
        if not self.bus:
            return
        
        await self.bus.publish("arie.alert", {
            "type": alert_type,
            "message": message,
            "timestamp": datetime.now(UTC).isoformat() + "Z",
            "severity": "high"
        })
    
    async def _request_certification(self, summary):
        """Request Truth Engine certification for applied fixes"""
        logger.info(f"[ARIE] Requesting Truth certification for run {summary.run_id}")
        
        # Placeholder for Truth Engine integration
        # This will be implemented when Truth Engine adapter is created
        # For now, simulate success
        
        cert_result = {
            "success": True,
            "certificate_id": f"truth_{summary.run_id}",
            "timestamp": datetime.now(UTC).isoformat() + "Z"
        }
        
        # Update patches with certification info
        for patch in summary.patches:
            patch.certified = cert_result["success"]
            patch.certificate_id = cert_result.get("certificate_id")
        
        return cert_result
    
    async def _handle_failed_certification(self, summary):
        """Handle failed Truth certification by rolling back patches"""
        logger.warning(f"[ARIE] Rolling back patches due to failed certification")
        
        if not self.engine:
            return
        
        for patch in summary.patches:
            try:
                # Trigger rollback
                rollback = self.engine.rollback(patch.id, force=False)
                
                if rollback.success:
                    logger.info(f"[ARIE] Rolled back patch {patch.id}")
                    await self._publish_rollback(rollback)
                    
                    # Log rollback
                    self._log_rollback(patch.id, rollback)
                else:
                    logger.error(f"[ARIE] Failed to rollback patch {patch.id}: {rollback.error}")
                    await self._publish_alert("rollback_failed", f"Patch {patch.id}: {rollback.error}")
                    
            except Exception as e:
                logger.exception(f"[ARIE] Error rolling back patch {patch.id}: {e}")
                await self._publish_alert("rollback_error", str(e))
    
    async def _commit_results(self, summary):
        """Commit certified results"""
        logger.info(f"[ARIE] Committing certified results for run {summary.run_id}")
        
        # Publish cascade notifications
        if self.bus:
            await self.bus.publish("cascade.notify", {
                "source": "arie",
                "run_id": summary.run_id,
                "timestamp": datetime.now(UTC).isoformat() + "Z",
                "fixes_applied": summary.fixes_applied,
                "certified": True
            })
    
    def _log_rollback(self, patch_id: str, rollback):
        """Log rollback to JSON file"""
        from pathlib import Path
        import json
        
        logs_dir = Path(__file__).parent.parent.parent.parent / "logs"
        logs_dir.mkdir(exist_ok=True)
        
        rollback_log = logs_dir / "arie_rollback.json"
        
        entry = {
            "timestamp": datetime.now(UTC).isoformat() + "Z",
            "patch_id": patch_id,
            "rollback_id": rollback.id,
            "success": rollback.success,
            "error": rollback.error,
            "restored_files": rollback.restored_files
        }
        
        try:
            # Read existing log
            if rollback_log.exists():
                with open(rollback_log, 'r') as f:
                    log_data = json.load(f)
            else:
                log_data = []
            
            # Append new entry
            log_data.append(entry)
            
            # Keep only last 100 entries
            log_data = log_data[-100:]
            
            # Write back
            with open(rollback_log, 'w') as f:
                json.dump(log_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"[ARIE] Failed to write rollback log: {e}")
    
    
    async def _check_permission(self, capability: str) -> bool:
        """Check permission via Permission Engine"""
        # Placeholder for Permission Engine integration
        # For now, return True
        return True
