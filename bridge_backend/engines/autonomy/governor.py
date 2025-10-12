"""
Autonomy Governor - Policy brain for autonomous decision-making

Evaluates incidents/events and chooses actions using a scored policy matrix.
Includes rate limiting, cooldowns, and circuit breaker for safety.
"""

import os
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List
from .models import Incident, Decision

logger = logging.getLogger(__name__)


class AutonomyGovernor:
    """
    Autonomy Governor - Makes autonomous healing decisions with safety guardrails
    
    Features:
    - Policy-based decision making
    - Rate limiting (max actions per hour)
    - Cooldown period between actions
    - Circuit breaker (auto-off after N consecutive failed heals)
    """
    
    def __init__(self, now=None):
        self.now = now or datetime.now(timezone.utc)
        self.window: List[datetime] = []
        self.max_actions_per_hour = int(os.getenv("AUTONOMY_MAX_ACTIONS_PER_HOUR", "6"))
        self.cooldown = timedelta(minutes=int(os.getenv("AUTONOMY_COOLDOWN_MINUTES", "5")))
        self.last_action_at: Optional[datetime] = None
        self.fail_streak = 0
        self.fail_streak_trip = int(os.getenv("AUTONOMY_FAIL_STREAK_TRIP", "3"))  # circuit breaker
    
    async def decide(self, incident: Incident) -> Decision:
        """
        Decide what action to take for an incident
        
        Args:
            incident: The incident to evaluate
            
        Returns:
            Decision object with action, reason, and targets
        """
        # Circuit breaker check
        if self.fail_streak >= self.fail_streak_trip:
            logger.warning(f"[Governor] Circuit breaker tripped (fail_streak={self.fail_streak})")
            return Decision(action="ESCALATE", reason="circuit_breaker_tripped")
        
        # Rate limiting check
        cutoff = self.now - timedelta(hours=1)
        self.window = [t for t in self.window if t >= cutoff]
        if len(self.window) >= self.max_actions_per_hour:
            logger.info(f"[Governor] Rate limited ({len(self.window)} actions in last hour)")
            return Decision(action="NOOP", reason="rate_limited")
        
        # Cooldown check
        if self.last_action_at and self.now - self.last_action_at < self.cooldown:
            logger.info(f"[Governor] In cooldown period")
            return Decision(action="NOOP", reason="cooldown")
        
        # Policy matrix - simple incident-to-action mapping
        # Can be extended with HXO signals and more sophisticated scoring
        if incident.kind == "deploy.netlify.preview_failed":
            return Decision(action="REPAIR_CONFIG", targets=["netlify"], reason="preview_failed")
        
        if incident.kind in ("deploy.render.failed", "deploy.render.rollback"):
            return Decision(action="RETRY", reason="render_retry_once")
        
        if incident.kind == "env.drift.detected":
            return Decision(action="SYNC_ENVS", reason="env_drift")
        
        if incident.kind == "envrecon.drift":
            return Decision(action="SYNC_ENVS", reason="envrecon_drift")
        
        if incident.kind == "code.integrity.deprecated":
            return Decision(action="REPAIR_CODE", reason="arie_safe_edit")
        
        if incident.kind == "arie.deprecated.detected":
            return Decision(action="REPAIR_CODE", reason="arie_safe_edit")
        
        # Unknown incident kind
        logger.warning(f"[Governor] Unrecognized incident kind: {incident.kind}")
        return Decision(action="NOOP", reason="unrecognized_incident")
    
    async def execute(self, decision: Decision) -> Dict[str, Any]:
        """
        Execute a decision and update governor state
        
        Args:
            decision: The decision to execute
            
        Returns:
            Execution result dictionary
        """
        from bridge_backend.genesis.bus import genesis_bus
        
        # Record action in window
        self.window.append(self.now)
        self.last_action_at = self.now
        
        try:
            # Execute based on action type
            if decision.action == "REPAIR_CONFIG":
                report = await self._repair_config(decision.targets or ["netlify"])
            elif decision.action == "REPAIR_CODE":
                report = await self._repair_code()
            elif decision.action == "SYNC_ENVS":
                report = await self._sync_envs()
            elif decision.action == "RETRY":
                report = await self._retry_deploy()
            elif decision.action == "ROLLBACK":
                report = await self._rollback()
            else:
                return {"status": "skipped", "reason": decision.reason}
            
            # Certify with Truth Engine
            certified = await self._certify(report)
            
            # Publish success event
            if genesis_bus.is_enabled():
                await genesis_bus.publish("autonomy.heal.applied", {
                    "decision": decision.model_dump(),
                    "certified": certified
                })
            
            # Update fail streak
            self.fail_streak = 0 if certified.get("ok") else self.fail_streak + 1
            
            return {"status": "applied", "certified": certified}
        
        except Exception as e:
            logger.exception(f"[Governor] Execution error: {e}")
            self.fail_streak += 1
            
            # Publish error event
            if genesis_bus.is_enabled():
                await genesis_bus.publish("autonomy.heal.error", {
                    "decision": decision.model_dump(),
                    "error": str(e)
                })
            
            return {"status": "error", "error": str(e)}
    
    async def _repair_config(self, platforms: List[str]) -> Dict[str, Any]:
        """Repair configuration using Chimera engine"""
        try:
            from bridge_backend.engines.chimera.core import ChimeraEngine
            chimera = ChimeraEngine()
            return await chimera.heal_config(platforms=platforms)
        except ImportError:
            # Fallback to bridge_core chimera
            try:
                from bridge_backend.bridge_core.engines.chimera.engine import ChimeraDeploymentEngine
                chimera = ChimeraDeploymentEngine()
                # Simulate config healing for the first platform
                platform = platforms[0] if platforms else "netlify"
                result = await chimera.simulate(platform)
                return {"status": "simulated", "platform": platform, "result": result}
            except Exception as e:
                logger.error(f"[Governor] Chimera import failed: {e}")
                return {"status": "error", "error": str(e)}
    
    async def _repair_code(self) -> Dict[str, Any]:
        """Repair code using ARIE engine"""
        try:
            from bridge_backend.engines.arie.core import ARIEEngine
            arie = ARIEEngine()
            return await arie.apply(policy="SAFE_EDIT", dry_run=False)
        except ImportError:
            logger.error("[Governor] ARIE engine not available")
            return {"status": "error", "error": "ARIE engine not available"}
        except Exception as e:
            logger.error(f"[Governor] ARIE execution failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _sync_envs(self) -> Dict[str, Any]:
        """Sync environments using EnvRecon engine"""
        try:
            from bridge_backend.engines.envrecon.core import EnvReconEngine
            envrecon = EnvReconEngine()
            return await envrecon.sync(intent_only=False)
        except ImportError:
            logger.error("[Governor] EnvRecon engine not available")
            return {"status": "error", "error": "EnvRecon engine not available"}
        except Exception as e:
            logger.error(f"[Governor] EnvRecon execution failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _retry_deploy(self) -> Dict[str, Any]:
        """Retry last deployment using Chimera engine"""
        try:
            from bridge_backend.engines.chimera.core import ChimeraEngine
            chimera = ChimeraEngine()
            return await chimera.retry_last_deploy()
        except ImportError:
            logger.error("[Governor] Chimera engine not available for retry")
            return {"status": "error", "error": "Chimera engine not available"}
        except Exception as e:
            logger.error(f"[Governor] Chimera retry failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _rollback(self) -> Dict[str, Any]:
        """Rollback using Chimera engine"""
        try:
            from bridge_backend.engines.chimera.core import ChimeraEngine
            chimera = ChimeraEngine()
            return await chimera.rollback()
        except ImportError:
            logger.error("[Governor] Chimera engine not available for rollback")
            return {"status": "error", "error": "Chimera engine not available"}
        except Exception as e:
            logger.error(f"[Governor] Chimera rollback failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _certify(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """Certify result using Truth Engine"""
        try:
            from bridge_backend.bridge_core.engines.truth.core import TruthEngine
            truth = TruthEngine()
            result = await truth.certify(report)
            return {"ok": result.get("certified", False), "result": result}
        except ImportError:
            logger.warning("[Governor] Truth engine not available, assuming OK")
            return {"ok": True, "result": {"certified": True, "reason": "truth_engine_unavailable"}}
        except Exception as e:
            logger.error(f"[Governor] Truth certification failed: {e}")
            return {"ok": False, "result": {"certified": False, "error": str(e)}}
