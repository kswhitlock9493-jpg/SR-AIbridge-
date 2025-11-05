"""
Chimera Oracle - Predictive Deploy Engine
Main orchestration engine for autonomous deployment with certification
Extends existing ChimeraEngine with v1.9.7i capabilities
"""

import os
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any
import logging

from .preflight.netlify_config import (
    write_headers, write_redirects, write_netlify_toml, 
    RedirectRule, DEFAULT_SECURITY_HEADERS
)
from .planner import DecisionMatrix
from .adapters.leviathan_adapter import LeviathanAdapter
from .adapters.truth_adapter import TruthGate
from .adapters.arie_adapter import ArieGate
from .adapters.env_adapter import EnvSuite
from .adapters.github_forge_adapter import GitHubForge
from .adapters.netlify_guard_adapter import NetlifyGuard
# Legacy Render fallback adapter removed - using BRH sovereign deployment
# from .adapters.render_fallback_adapter import RenderFallback

logger = logging.getLogger(__name__)

DIST_GUESS = ["frontend/dist", "frontend/build", "apps/web/out", "dist", "build", "bridge-frontend/dist"]


def require_role(role: str):
    """
    Simple RBAC decorator for Chimera operations
    In production, this would integrate with proper auth system
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # For now, check environment variable or allow all
            rbac_enforced = os.getenv("RBAC_ENFORCED", "false").lower() == "true"
            if rbac_enforced:
                # In production, verify JWT/session role
                # For now, proceed if admiral role required
                pass
            return await func(*args, **kwargs)
        return wrapper
    return decorator


class ChimeraEngine:
    """Chimera deployment healing engine (legacy support)"""
    
    def __init__(self, repo_root: Path = None):
        self.root = repo_root or Path.cwd()
        
    def detect_publish_dir(self) -> str:
        """Auto-detect publish directory"""
        for p in DIST_GUESS:
            if (self.root / p).exists():
                return p
        return "frontend/build"
    
    async def preflight(self) -> dict:
        """Run preflight validation and generate deploy artifacts"""
        try:
            # Import genesis_bus here to avoid circular imports
            from ...genesis.bus import genesis_bus
            await genesis_bus.publish("chimera.preflight.start", {})
        except Exception as e:
            logger.warning(f"Failed to publish chimera.preflight.start: {e}")
        
        publish = self.detect_publish_dir()
        headers = DEFAULT_SECURITY_HEADERS
        redirects = [
            RedirectRule(from_path="/api/*", to_path="/.netlify/functions/server", status=200),
            RedirectRule(from_path="/*", to_path="/index.html", status=200)
        ]
        
        # Generate files
        write_headers(self.root, headers)
        write_redirects(self.root, redirects)
        write_netlify_toml(self.root, publish)
        
        # Quick syntax smoke-checks
        assert (self.root / "_headers").stat().st_size > 0, "_headers file is empty"
        assert (self.root / "_redirects").stat().st_size > 0, "_redirects file is empty"
        assert (self.root / "netlify.toml").stat().st_size > 0, "netlify.toml file is empty"
        
        payload = {"publish": publish, "status": "ok"}
        
        try:
            from ...genesis.bus import genesis_bus
            await genesis_bus.publish("chimera.preflight.ok", payload)
        except Exception as e:
            logger.warning(f"Failed to publish chimera.preflight.ok: {e}")
        
        return payload
    
    async def heal_after_failure(self, reason: str) -> None:
        """Heal after deployment failure"""
        intent = {"reason": reason}
        
        try:
            from ...genesis.bus import genesis_bus
            await genesis_bus.publish("chimera.deploy.heal.intent", intent)
        except Exception as e:
            logger.warning(f"Failed to publish chimera.deploy.heal.intent: {e}")
        
        # Regenerate with safe defaults
        await self.preflight()
        
        try:
            from ...genesis.bus import genesis_bus
            await genesis_bus.publish("chimera.deploy.heal.applied", intent)
        except Exception as e:
            logger.warning(f"Failed to publish chimera.deploy.heal.applied: {e}")


class ChimeraOracle:
    """
    Chimera Oracle - Predictive Deployment Engine (v1.9.7i)
    
    Orchestrates:
    - Environment audit and healing
    - Build simulation (Leviathan)
    - Configuration synthesis (Hydra)
    - Truth certification
    - Deploy execution with fallback
    """
    
    def __init__(self):
        self.dm = DecisionMatrix()
        self.lev = LeviathanAdapter()
        self.truth = TruthGate()
        self.arie = ArieGate()
        self.env = EnvSuite()
        self.guard = NetlifyGuard()
        # Legacy Render fallback removed - using BRH sovereign deployment
        # self.fallback = RenderFallback()
        self.forge = GitHubForge()
    
    @require_role("admiral")
    async def run(self, ref: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute predictive deployment pipeline
        
        Args:
            ref: Deployment reference (commit SHA, branch, etc.)
            
        Returns:
            Deployment outcome
        """
        # Import genesis_bus only when needed to avoid circular imports
        try:
            from ...genesis.bus import genesis_bus
        except ImportError:
            genesis_bus = None
        
        # 1) Env audit + heal intent
        audit = await self.env.audit()
        if audit.get("has_drift"):
            if genesis_bus:
                await genesis_bus.publish("env.heal.intent", audit)
            # best-effort local correction (safe mode)
            await self.env.apply_local_intent(audit)
        
        # 2) Simulation
        sim = await self.lev.simulate(ref)
        if genesis_bus:
            await genesis_bus.publish("deploy.simulate", sim)
        
        if not sim.get("can_build"):
            return {
                "status": "blocked",
                "reason": "simulation-failed",
                "details": sim
            }
        
        # 3) Guard Netlify config (synthesize/repair)
        guard = await self.guard.synthesize_and_validate()
        if genesis_bus:
            await genesis_bus.publish("deploy.guard.netlify", guard)
        
        if not guard["ok"]:
            # Give ARIE a chance to fix structure-level issues
            fix_report = await self.arie.safe_fix(guard)
            if genesis_bus:
                await genesis_bus.publish("arie.fix.applied", fix_report)
        
        # 4) Truth + ARIE certification
        cert = await self.truth.certify(sim, guard)
        if genesis_bus:
            await genesis_bus.publish("deploy.certificate", cert)
        
        if not cert["ok"]:
            return {
                "status": "blocked",
                "reason": "truth-cert-failed",
                "cert": cert
            }
        
        # 5) Execute deploy (try Netlify, fallback Render)
        plan = self.dm.plan(sim, guard)
        if genesis_bus:
            await genesis_bus.publish("deploy.plan", plan)
        
        if plan["target"] == "netlify":
            outcome = await self.guard.deploy(plan)
            if not outcome["ok"]:
                fb = await self.fallback.deploy(plan)
                if genesis_bus:
                    await genesis_bus.publish("deploy.fallback.render", fb)
                outcome = fb
        else:
            outcome = await self.fallback.deploy(plan)
        
        topic = "deploy.outcome.success" if outcome["ok"] else "deploy.outcome.failure"
        if genesis_bus:
            await genesis_bus.publish(topic, outcome)
        
        return {
            "status": "ok" if outcome["ok"] else "failed",
            "outcome": outcome
        }
