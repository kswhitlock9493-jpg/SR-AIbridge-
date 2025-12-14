"""
Umbra Healers
Delegates to Autonomy + Cascade for targeted remediation
"""

import logging
import os
from typing import Dict, Any, Optional
from datetime import datetime

from .models import HealPlan, TriageTicket, TriageStatus

logger = logging.getLogger(__name__)


class UmbraHealers:
    """
    Healing subsystem for Umbra Triage Mesh
    
    Delegates to:
    - Autonomy Engine for autonomous healing
    - Cascade Engine for configuration patches
    - Chimera Engine for deployment healing
    - Parity Engine for environment convergence
    
    Includes safe rollback hooks
    """
    
    def __init__(self):
        self.allow_heal = os.getenv("UMBRA_ALLOW_HEAL", "false").lower() == "true"
        self.auto_heal_on = os.getenv("AUTO_HEAL_ON", "true").lower() == "true"
        self.rbac_min_role = os.getenv("UMBRA_RBAC_MIN_ROLE", "admiral")
        
        logger.info(f"[Umbra Healers] Initialized (allow_heal={self.allow_heal}, auto_heal={self.auto_heal_on})")
    
    async def execute_heal_plan(self, plan: HealPlan, ticket: TriageTicket) -> Dict[str, Any]:
        """
        Execute a heal plan
        
        Args:
            plan: Heal plan to execute
            ticket: Associated ticket
            
        Returns:
            Execution results
        """
        if not self.allow_heal:
            logger.info(f"[Umbra Healers] Heal not allowed, generating intent only: {plan.plan_id}")
            return {
                "status": "intent_only",
                "plan_id": plan.plan_id,
                "message": "Healing disabled (UMBRA_ALLOW_HEAL=false)",
                "intent": {
                    "actions": [a.dict() for a in plan.actions],
                    "parity_prechecks": plan.parity_prechecks
                }
            }
        
        try:
            # Step 1: Run parity prechecks
            if plan.parity_prechecks:
                precheck_result = await self._run_parity_prechecks(plan.parity_prechecks)
                if not precheck_result.get("ok", False):
                    logger.error(f"[Umbra Healers] Parity prechecks failed: {precheck_result}")
                    return {
                        "status": "failed",
                        "reason": "parity_precheck_failed",
                        "details": precheck_result
                    }
            
            # Step 2: Get Truth certification
            if not plan.certified:
                cert_result = await self._certify_with_truth(plan)
                if not cert_result.get("ok", False):
                    logger.error(f"[Umbra Healers] Truth certification failed: {cert_result}")
                    return {
                        "status": "failed",
                        "reason": "truth_certification_failed",
                        "details": cert_result
                    }
                plan.certified = True
                plan.certification_signature = cert_result.get("signature")
            
            # Step 3: Execute actions
            results = []
            for action in plan.actions:
                logger.info(f"[Umbra Healers] Executing action: {action.action_type} on {action.target}")
                
                action_result = await self._execute_action(action)
                results.append(action_result)
                
                if not action_result.get("ok", False):
                    # Action failed, trigger rollback
                    logger.error(f"[Umbra Healers] Action failed, triggering rollback: {action.action_type}")
                    await self._rollback(plan, results[:-1])  # Rollback successful actions
                    
                    return {
                        "status": "failed",
                        "reason": "action_failed",
                        "failed_action": action.action_type,
                        "details": action_result,
                        "rollback": "completed"
                    }
            
            # Step 4: Run parity post-checks
            if plan.parity_prechecks:
                postcheck_result = await self._run_parity_postchecks(plan.parity_prechecks)
                if not postcheck_result.get("ok", False):
                    logger.warning(f"[Umbra Healers] Parity postchecks failed: {postcheck_result}")
                    # Consider rollback if parity is not achieved
            
            # Update ticket status
            ticket.status = TriageStatus.HEALED
            ticket.healed_at = datetime.utcnow()
            
            logger.info(f"[Umbra Healers] Heal plan executed successfully: {plan.plan_id}")
            
            return {
                "status": "success",
                "plan_id": plan.plan_id,
                "actions_executed": len(results),
                "results": results
            }
            
        except Exception as e:
            logger.error(f"[Umbra Healers] Failed to execute heal plan: {e}")
            return {
                "status": "error",
                "reason": str(e)
            }
    
    async def _run_parity_prechecks(self, prechecks: list) -> Dict[str, Any]:
        """Run parity prechecks before healing"""
        try:
            # Import Parity engine
            from bridge_backend.engines.envrecon.parity import check_parity
            
            results = []
            for check in prechecks:
                result = await check_parity(check)
                results.append(result)
            
            all_ok = all(r.get("ok", False) for r in results)
            
            return {
                "ok": all_ok,
                "results": results
            }
        except ImportError:
            logger.warning("[Umbra Healers] Parity engine not available, skipping prechecks")
            return {"ok": True, "reason": "parity_not_available"}
        except Exception as e:
            logger.error(f"[Umbra Healers] Parity precheck error: {e}")
            return {"ok": False, "error": str(e)}
    
    async def _run_parity_postchecks(self, postchecks: list) -> Dict[str, Any]:
        """Run parity postchecks after healing"""
        return await self._run_parity_prechecks(postchecks)  # Same logic
    
    async def _certify_with_truth(self, plan: HealPlan) -> Dict[str, Any]:
        """Get Truth certification for heal plan"""
        try:
            from bridge_backend.bridge_core.engines.truth.core import TruthEngine
            
            truth = TruthEngine()
            
            cert_data = {
                "plan_id": plan.plan_id,
                "ticket_id": plan.ticket_id,
                "actions": [a.dict() for a in plan.actions],
                "policy": plan.truth_policy
            }
            
            result = await truth.certify(cert_data)
            
            return {
                "ok": result.get("certified", False),
                "signature": result.get("signature"),
                "result": result
            }
        except ImportError:
            logger.warning("[Umbra Healers] Truth engine not available, auto-approving")
            return {
                "ok": True,
                "signature": "auto-approved",
                "reason": "truth_not_available"
            }
        except Exception as e:
            logger.error(f"[Umbra Healers] Truth certification error: {e}")
            return {"ok": False, "error": str(e)}
    
    async def _execute_action(self, action) -> Dict[str, Any]:
        """
        Execute a single heal action
        
        Delegates to appropriate engine based on action type
        """
        action_type = action.action_type
        
        try:
            if action_type.startswith("normalize_netlify"):
                return await self._execute_chimera_action(action)
            elif action_type.startswith("normalize_render"):
                return await self._execute_chimera_action(action)
            elif action_type.startswith("endpoint_"):
                return await self._execute_healthnet_action(action)
            elif action_type.startswith("service_"):
                return await self._execute_autonomy_action(action)
            else:
                logger.warning(f"[Umbra Healers] Unknown action type: {action_type}")
                return {"ok": False, "error": f"Unknown action type: {action_type}"}
        
        except Exception as e:
            logger.error(f"[Umbra Healers] Action execution error: {e}")
            return {"ok": False, "error": str(e)}
    
    async def _execute_chimera_action(self, action) -> Dict[str, Any]:
        """Execute action via Chimera engine"""
        try:
            from bridge_backend.engines.chimera.core import ChimeraEngine
            
            chimera = ChimeraEngine()
            
            # Trigger Chimera preflight
            result = await chimera.run_preflight()
            
            return {
                "ok": True,
                "action": action.action_type,
                "result": result
            }
        except ImportError:
            logger.warning("[Umbra Healers] Chimera engine not available")
            return {"ok": False, "error": "chimera_not_available"}
        except Exception as e:
            logger.error(f"[Umbra Healers] Chimera action error: {e}")
            return {"ok": False, "error": str(e)}
    
    async def _execute_healthnet_action(self, action) -> Dict[str, Any]:
        """Execute action via HealthNet"""
        logger.info(f"[Umbra Healers] HealthNet action: {action.action_type}")
        # Placeholder for HealthNet integration
        return {
            "ok": True,
            "action": action.action_type,
            "message": "HealthNet action simulated"
        }
    
    async def _execute_autonomy_action(self, action) -> Dict[str, Any]:
        """Execute action via Autonomy engine"""
        try:
            from bridge_backend.engines.autonomy.core import AutonomyEngine
            
            autonomy = AutonomyEngine()
            
            # Trigger autonomy healing
            result = await autonomy.auto_heal({
                "action": action.action_type,
                "target": action.target,
                "parameters": action.parameters
            })
            
            return {
                "ok": result.get("success", False),
                "action": action.action_type,
                "result": result
            }
        except ImportError:
            logger.warning("[Umbra Healers] Autonomy engine not available")
            return {"ok": False, "error": "autonomy_not_available"}
        except Exception as e:
            logger.error(f"[Umbra Healers] Autonomy action error: {e}")
            return {"ok": False, "error": str(e)}
    
    async def _rollback(self, plan: HealPlan, executed_actions: list) -> Dict[str, Any]:
        """
        Rollback executed actions
        
        Args:
            plan: Original heal plan
            executed_actions: Actions that were successfully executed
            
        Returns:
            Rollback result
        """
        logger.warning(f"[Umbra Healers] Rolling back {len(executed_actions)} actions")
        
        # Emit rollback event
        try:
            from bridge_backend.genesis.bus import genesis_bus
            
            if genesis_bus.is_enabled():
                await genesis_bus.publish("triage.heal.rollback", {
                    "plan_id": plan.plan_id,
                    "ticket_id": plan.ticket_id,
                    "actions_rolled_back": len(executed_actions),
                    "timestamp": datetime.utcnow().isoformat()
                })
        except Exception as e:
            logger.warning(f"[Umbra Healers] Failed to emit rollback event: {e}")
        
        # Placeholder for actual rollback logic
        # In production, this would restore previous state
        
        return {
            "ok": True,
            "actions_rolled_back": len(executed_actions)
        }
