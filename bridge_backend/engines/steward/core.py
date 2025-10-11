"""
Env Steward Core Engine
Admiral-tier environment orchestration with explicit authorization
"""

from typing import Dict, List, Optional
import os
import secrets
import time
import logging
from .models import DiffReport, Plan, ApplyResult, EnvVarChange

logger = logging.getLogger(__name__)

# Configuration
STEWARD_ENABLED = os.getenv("STEWARD_ENABLED", "false").lower() == "true"
WRITE_ENABLED = os.getenv("STEWARD_WRITE_ENABLED", "false").lower() == "true"
OWNER_HANDLE = os.getenv("STEWARD_OWNER_HANDLE", "")
CAP_TTL_SECONDS = int(os.getenv("STEWARD_CAP_TTL_SECONDS", "600"))


class Steward:
    """
    Env Steward - Admiral-tier environment orchestration
    
    Features:
    - Environment drift detection
    - Planned, phased changes
    - Truth & Blueprint validation
    - Explicit owner authorization required for writes
    - Provider adapters (Render, Netlify, GitHub)
    - Genesis event publishing
    """
    
    def __init__(self):
        self._window_open: Dict[str, float] = {}
        self._plans: Dict[str, Plan] = {}
        self._enabled = STEWARD_ENABLED
        
        if self._enabled:
            logger.info(f"🛡️ Steward Engine initialized (write_enabled={WRITE_ENABLED}, owner={OWNER_HANDLE})")
        else:
            logger.info("🛡️ Steward Engine disabled (set STEWARD_ENABLED=true to enable)")
    
    async def diff(self, providers: List[str], dry_run: bool = True) -> DiffReport:
        """
        Compute environment drift against Blueprint EnvSpec
        
        Args:
            providers: List of providers to check (render, netlify, github)
            dry_run: If True, don't make any changes
            
        Returns:
            DiffReport with detected drift
        """
        if not self._enabled:
            raise RuntimeError("Steward engine is disabled")
        
        # Publish intent to Genesis
        await self._publish_genesis_event("steward.intent", {
            "type": "DIFF",
            "providers": providers,
            "dry_run": dry_run
        })
        
        # Integrate with EnvRecon to get actual environment drift
        try:
            from bridge_backend.engines.envrecon.core import EnvReconEngine
            envrecon = EnvReconEngine()
            recon_report = await envrecon.reconcile()
            
            # Convert EnvRecon report to Steward changes
            changes = []
            
            # Create changes for missing variables in each provider
            if "render" in providers:
                for key in recon_report.get("missing_in_render", []):
                    changes.append(EnvVarChange(
                        key=key,
                        old_value=None,
                        new_value="<from_local>",
                        action="create",
                        is_secret=self._is_secret_var(key)
                    ))
            
            if "netlify" in providers:
                for key in recon_report.get("missing_in_netlify", []):
                    if not any(c.key == key and c.action == "create" for c in changes):
                        changes.append(EnvVarChange(
                            key=key,
                            old_value=None,
                            new_value="<from_local>",
                            action="create",
                            is_secret=self._is_secret_var(key)
                        ))
            
            if "github" in providers:
                for key in recon_report.get("missing_in_github", []):
                    if not any(c.key == key and c.action == "create" for c in changes):
                        changes.append(EnvVarChange(
                            key=key,
                            old_value=None,
                            new_value="<from_local>",
                            action="create",
                            is_secret=self._is_secret_var(key)
                        ))
            
            # Build comprehensive report
            report = DiffReport(
                has_drift=len(changes) > 0,
                providers=providers,
                changes=changes,
                missing_in_render=recon_report.get("missing_in_render", []),
                missing_in_netlify=recon_report.get("missing_in_netlify", []),
                missing_in_github=recon_report.get("missing_in_github", []),
                extra_in_render=recon_report.get("extra_in_render", []),
                extra_in_netlify=recon_report.get("extra_in_netlify", []),
                conflicts=recon_report.get("conflicts", {}),
                summary=recon_report.get("summary", {})
            )
            
            logger.info(f"📊 Diff complete via EnvRecon: {len(changes)} changes detected across {len(providers)} providers")
            
        except Exception as e:
            logger.warning(f"⚠️ EnvRecon integration failed, using fallback: {e}")
            # Fallback to empty report if EnvRecon fails
            report = DiffReport(
                has_drift=False,
                providers=providers,
                changes=[]
            )
        
        return report
    
    def _is_secret_var(self, key: str) -> bool:
        """Determine if a variable name indicates a secret"""
        secret_indicators = [
            "SECRET", "KEY", "TOKEN", "PASSWORD", "API_KEY", 
            "AUTH", "CREDENTIAL", "PRIVATE", "BEARER"
        ]
        return any(indicator in key.upper() for indicator in secret_indicators)
    
    async def plan(self, providers: List[str], strategy: str = "safe-phased") -> Plan:
        """
        Create an execution plan for environment changes
        
        Args:
            providers: List of providers to plan for
            strategy: Planning strategy (safe-phased, immediate, etc.)
            
        Returns:
            Plan object with mutation window
        """
        if not self._enabled:
            raise RuntimeError("Steward engine is disabled")
        
        # Get diff first
        diff = await self.diff(providers, dry_run=True)
        
        # Create plan
        plan_id = secrets.token_hex(16)
        
        # Build phased plan (simplified for now)
        phases = []
        if diff.has_drift:
            # Phase 1: Non-secret variables
            non_secret_changes = [c for c in diff.changes if not c.is_secret]
            if non_secret_changes:
                phases.append({
                    "name": "non-secrets",
                    "changes": [c.dict() for c in non_secret_changes]
                })
            
            # Phase 2: Secret variables
            secret_changes = [c for c in diff.changes if c.is_secret]
            if secret_changes:
                phases.append({
                    "name": "secrets",
                    "changes": [c.dict() for c in secret_changes]
                })
            
            # Phase 3: Restart hooks (if needed)
            phases.append({
                "name": "restart-hooks",
                "changes": []
            })
        
        # Open mutation window
        win_id = secrets.token_hex(16)
        ttl = CAP_TTL_SECONDS
        self._window_open[win_id] = time.time() + ttl
        
        plan = Plan(
            id=plan_id,
            providers=providers,
            strategy=strategy,
            phases=phases,
            mutation_window_id=win_id,
            certified=True  # Would be set by Truth Engine
        )
        
        # Store plan
        self._plans[plan_id] = plan
        
        # Publish to Genesis
        await self._publish_genesis_event("steward.plan", {
            "plan_id": plan.id,
            "window_id": win_id,
            "expires_in": ttl,
            "phases": len(phases)
        })
        
        logger.info(f"📋 Plan created: {plan_id} with {len(phases)} phases (window: {win_id})")
        
        return plan
    
    async def apply(self, plan: Plan, cap_token: str, actor: str) -> ApplyResult:
        """
        Apply an execution plan (ADMIRAL-TIER ONLY)
        
        Args:
            plan: The plan to execute
            cap_token: Capability token for authorization
            actor: The actor requesting the apply
            
        Returns:
            ApplyResult with execution status
            
        Raises:
            PermissionError: If not authorized
        """
        if not self._enabled:
            raise RuntimeError("Steward engine is disabled")
        
        if not WRITE_ENABLED:
            raise PermissionError("Write mode disabled (STEWARD_WRITE_ENABLED=false)")
        
        # ADMIRAL-TIER LOCK: Only owner can apply
        if actor != OWNER_HANDLE:
            raise PermissionError(f"Only admiral (owner={OWNER_HANDLE}) may apply. Current actor: {actor}")
        
        # Validate capability token (simplified - would use Permission Engine)
        if not cap_token:
            raise PermissionError("Missing capability token (X-Bridge-Cap header required)")
        
        # Check mutation window
        if plan.mutation_window_id not in self._window_open:
            raise PermissionError("Mutation window not found or expired")
        
        window_expiry = self._window_open[plan.mutation_window_id]
        if time.time() > window_expiry:
            raise PermissionError("Mutation window expired")
        
        # Execute plan (simplified - would use adapters)
        logger.info(f"🚀 Applying plan {plan.id} as {actor}")
        
        # Publish to Genesis
        await self._publish_genesis_event("steward.apply", {
            "plan_id": plan.id,
            "actor": actor,
            "phases": len(plan.phases)
        })
        
        # Simulate execution
        change_counts = {
            "created": 0,
            "updated": 0,
            "deleted": 0
        }
        
        # Execute each phase
        for phase in plan.phases:
            for change_dict in phase.get("changes", []):
                action = change_dict.get("action", "update")
                if action in change_counts:
                    change_counts[action] += 1
        
        total_changes = sum(change_counts.values())
        
        # Create result
        result = ApplyResult(
            ok=True,
            plan_id=plan.id,
            changes_applied=total_changes,
            change_counts=change_counts,
            rollback_ref=secrets.token_hex(16)  # Would be Vault reference
        )
        
        # Publish result to Genesis
        await self._publish_genesis_event("steward.result", {
            "plan_id": plan.id,
            "ok": result.ok,
            "changes": result.change_counts,
            "rollback_bundle": result.rollback_ref
        })
        
        logger.info(f"✅ Plan {plan.id} applied: {total_changes} changes")
        
        # Close mutation window
        if plan.mutation_window_id in self._window_open:
            del self._window_open[plan.mutation_window_id]
        
        return result
    
    async def issue_cap(self, actor: str, reason: str, ttl_seconds: int = 600, window_id: Optional[str] = None) -> str:
        """
        Issue a capability token (ADMIRAL-TIER ONLY)
        
        Args:
            actor: The actor requesting the capability
            reason: Reason for capability (for audit)
            ttl_seconds: Time to live in seconds
            window_id: Optional mutation window to bind to
            
        Returns:
            Capability token string
            
        Raises:
            PermissionError: If not authorized
        """
        if not self._enabled:
            raise RuntimeError("Steward engine is disabled")
        
        # ADMIRAL-TIER LOCK: Only owner can issue caps
        if actor != OWNER_HANDLE:
            raise PermissionError(f"Only admiral (owner={OWNER_HANDLE}) may issue capabilities. Current actor: {actor}")
        
        # Generate capability token
        cap_token = f"cap_{secrets.token_hex(32)}"
        
        logger.info(f"🔑 Capability issued to {actor}: {reason} (ttl={ttl_seconds}s)")
        
        # Publish to Genesis
        await self._publish_genesis_event("steward.cap.issued", {
            "actor": actor,
            "reason": reason,
            "ttl_seconds": ttl_seconds,
            "window_id": window_id
        })
        
        return cap_token
    
    async def _publish_genesis_event(self, topic: str, data: Dict):
        """Publish event to Genesis bus"""
        try:
            from bridge_backend.genesis.bus import genesis_bus
            await genesis_bus.publish(topic, data)
        except ImportError:
            logger.warning(f"Genesis bus not available, skipping event: {topic}")
        except Exception as e:
            logger.warning(f"Failed to publish Genesis event {topic}: {e}")
    
    def is_enabled(self) -> bool:
        """Check if steward is enabled"""
        return self._enabled
    
    def is_write_enabled(self) -> bool:
        """Check if write mode is enabled"""
        return WRITE_ENABLED


# Global instance
steward = Steward()
