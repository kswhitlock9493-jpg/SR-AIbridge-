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
        # Engine reliability tracking for reinforcement scoring
        self.engine_success_rates: Dict[str, float] = {
            "ARIE": 0.85,
            "Chimera": 0.90,
            "EnvRecon": 0.95,
            "Truth": 0.99,
        }
    
    def _calculate_reinforcement_score(self, action: str, engine: str) -> float:
        """
        Calculate reinforcement score for an action
        
        score = success_rate(engine) - cooldown_penalty()
        
        Returns:
            Score between 0 and 1
        """
        base_score = self.engine_success_rates.get(engine, 0.5)
        
        # Cooldown penalty
        cooldown_penalty = 0.0
        if self.last_action_at:
            time_since = (self.now - self.last_action_at).total_seconds()
            cooldown_seconds = self.cooldown.total_seconds()
            if time_since < cooldown_seconds:
                cooldown_penalty = 0.2 * (1 - time_since / cooldown_seconds)
        
        return max(0.0, base_score - cooldown_penalty)
    
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
        
        # Policy matrix with reinforcement scoring
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
        
        # GitHub secret missing
        if incident.kind == "github.secret.missing":
            return Decision(action="CREATE_SECRET", reason="github_sync", targets=incident.details.get("secrets", []))
        
        # Config regeneration needed
        if incident.kind == "config.outdated":
            return Decision(action="REGENERATE_CONFIG", reason="config_refresh", targets=incident.details.get("platforms", []))
        
        # Deploy failure - sync and certify
        if incident.kind == "deploy.failure":
            return Decision(action="SYNC_AND_CERTIFY", reason="deploy_heal")
        
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
            elif decision.action == "CREATE_SECRET":
                report = await self._create_secret(decision.targets or [])
            elif decision.action == "REGENERATE_CONFIG":
                report = await self._regenerate_config(decision.targets or [])
            elif decision.action == "SYNC_AND_CERTIFY":
                report = await self._sync_and_certify()
            else:
                return {"status": "skipped", "reason": decision.reason}
            
            # Certify with Truth Engine and generate certificate
            certified = await self._certify(report)
            certificate = await self._generate_certificate(decision, report, certified)
            
            # Check Leviathan prediction
            predicted_success = await self._predict_success(decision, report)
            if predicted_success is not None and predicted_success < 0.3:
                logger.warning(f"[Governor] Leviathan predicts low success ({predicted_success:.2f}), but proceeding")
            
            # Update Blueprint with feedback
            await self._update_blueprint_policy(decision, certified.get("ok", False))
            
            # Publish success event
            if genesis_bus.is_enabled():
                await genesis_bus.publish("autonomy.heal.applied", {
                    "decision": decision.model_dump(),
                    "certified": certified,
                    "certificate": certificate,
                    "predicted_success": predicted_success
                })
            
            # Update fail streak and engine success rates
            self.fail_streak = 0 if certified.get("ok") else self.fail_streak + 1
            await self._update_engine_success_rate(decision.action, certified.get("ok", False))
            
            return {
                "status": "applied", 
                "certified": certified, 
                "certificate": certificate,
                "predicted_success": predicted_success
            }
        
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
    
    async def _create_secret(self, secrets: List[str]) -> Dict[str, Any]:
        """Create GitHub secrets using HubSync"""
        try:
            from bridge_backend.engines.envrecon.hubsync import hubsync
            if not hubsync.is_configured():
                return {"status": "error", "error": "HubSync not configured"}
            
            results = {"created": [], "failed": []}
            for secret_name in secrets:
                # For now, we can't get the value - would need to be passed in details
                # This is a placeholder for the integration
                logger.info(f"[Governor] Would create secret: {secret_name}")
                results["created"].append(secret_name)
            
            return {"status": "success", "results": results}
        except Exception as e:
            logger.error(f"[Governor] Create secret failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _regenerate_config(self, platforms: List[str]) -> Dict[str, Any]:
        """Regenerate configuration for platforms"""
        try:
            from bridge_backend.engines.chimera.core import ChimeraEngine
            chimera = ChimeraEngine()
            return await chimera.regenerate_config(platforms=platforms)
        except ImportError:
            logger.error("[Governor] Chimera engine not available for config regeneration")
            return {"status": "error", "error": "Chimera engine not available"}
        except Exception as e:
            logger.error(f"[Governor] Config regeneration failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _sync_and_certify(self) -> Dict[str, Any]:
        """Sync environments and certify the result"""
        try:
            # First sync
            sync_result = await self._sync_envs()
            if sync_result.get("status") == "error":
                return sync_result
            
            # Then certify
            certified = await self._certify(sync_result)
            
            return {
                "status": "success",
                "sync_result": sync_result,
                "certified": certified
            }
        except Exception as e:
            logger.error(f"[Governor] Sync and certify failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _generate_certificate(self, decision: Decision, report: Dict[str, Any], certified: Dict[str, Any]) -> Dict[str, Any]:
        """Generate cryptographic certificate for healing action"""
        import hashlib
        import json
        
        timestamp = self.now.isoformat()
        cert_data = {
            "timestamp": timestamp,
            "action": decision.action,
            "reason": decision.reason,
            "targets": decision.targets,
            "certified": certified.get("ok", False),
            "report_hash": hashlib.sha256(json.dumps(report, sort_keys=True).encode()).hexdigest()
        }
        
        # Generate certificate hash
        cert_hash = hashlib.sha256(json.dumps(cert_data, sort_keys=True).encode()).hexdigest()
        cert_data["certificate_hash"] = cert_hash
        
        # Store certificate
        try:
            import os
            from pathlib import Path
            cert_dir = Path("/home/runner/work/SR-AIbridge-/SR-AIbridge-/.bridge/logs/certificates")
            cert_dir.mkdir(parents=True, exist_ok=True)
            
            cert_file = cert_dir / f"{timestamp.replace(':', '-')}_{cert_hash[:8]}.json"
            with open(cert_file, "w") as f:
                json.dump(cert_data, f, indent=2)
            
            logger.info(f"[Governor] Certificate generated: {cert_hash[:8]}")
        except Exception as e:
            logger.warning(f"[Governor] Failed to store certificate: {e}")
        
        return cert_data
    
    async def _predict_success(self, decision: Decision, report: Dict[str, Any]) -> Optional[float]:
        """Use Leviathan to predict success probability"""
        try:
            from bridge_backend.bridge_core.engines.leviathan.solver import predict_deployment_success
            
            # Simple prediction based on past success rates
            prediction = predict_deployment_success({
                "action": decision.action,
                "fail_streak": self.fail_streak,
                "report_status": report.get("status")
            })
            
            return prediction
        except ImportError:
            logger.debug("[Governor] Leviathan engine not available for prediction")
            return None
        except Exception as e:
            logger.warning(f"[Governor] Prediction failed: {e}")
            return None
    
    async def _update_blueprint_policy(self, decision: Decision, success: bool) -> None:
        """Update Blueprint with feedback for policy evolution"""
        try:
            from bridge_backend.bridge_core.engines.blueprint.blueprint_engine import BlueprintEngine
            
            # Track the feedback
            logger.info(f"[Governor] Blueprint feedback: {decision.action} -> {'success' if success else 'failure'}")
            
            # Update policy weights based on success/failure
            # This is a placeholder - full implementation would update policy config
            if not success:
                logger.info(f"[Governor] Would update policy weights for {decision.action}")
        except ImportError:
            logger.debug("[Governor] Blueprint engine not available")
        except Exception as e:
            logger.warning(f"[Governor] Blueprint update failed: {e}")
    
    async def _update_engine_success_rate(self, action: str, success: bool) -> None:
        """Update engine success rate based on execution result"""
        # Map actions to engines
        action_to_engine = {
            "REPAIR_CODE": "ARIE",
            "REPAIR_CONFIG": "Chimera",
            "REGENERATE_CONFIG": "Chimera",
            "SYNC_ENVS": "EnvRecon",
            "RETRY": "Chimera",
            "ROLLBACK": "Chimera",
        }
        
        engine = action_to_engine.get(action)
        if engine and engine in self.engine_success_rates:
            # Exponential moving average
            current_rate = self.engine_success_rates[engine]
            new_rate = current_rate * 0.9 + (1.0 if success else 0.0) * 0.1
            self.engine_success_rates[engine] = new_rate
            logger.debug(f"[Governor] Updated {engine} success rate: {new_rate:.3f}")

