"""
Sanctum Engine - Predictive Deployment Simulation Layer
Runs virtual deployment checks before actual deployment
"""

import os
import logging
import subprocess
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime, UTC

logger = logging.getLogger(__name__)


class SimulationReport:
    """Report from deployment simulation"""
    
    def __init__(self, can_build: bool = True, routes_ok: bool = True, 
                 config_ok: bool = True, errors: Optional[list] = None):
        self.can_build = can_build
        self.routes_ok = routes_ok
        self.config_ok = config_ok
        self.errors = errors or []
        self._timestamp = datetime.now(UTC).isoformat() + "Z"
    
    def has_errors(self) -> bool:
        """Check if simulation detected errors"""
        return not (self.can_build and self.routes_ok and self.config_ok)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for event publishing"""
        return {
            "can_build": self.can_build,
            "routes_ok": self.routes_ok,
            "config_ok": self.config_ok,
            "errors": self.errors,
            "timestamp": self._timestamp,
            "status": "failed" if self.has_errors() else "passed"
        }


class SanctumEngine:
    """
    Sanctum Predictive Simulation Engine
    
    Simulates deployment environment to catch issues before they occur.
    Integrates with Genesis Bus, Cascade, Truth, and Forge engines.
    """
    
    def __init__(self, repo_root: Optional[Path] = None):
        self.repo_root = repo_root or Path.cwd()
        self.enabled = os.getenv("SANCTUM_ENABLED", "true").lower() == "true"
    
    def _check_netlify_config(self) -> tuple[bool, list]:
        """Check Netlify configuration files"""
        errors = []
        
        # Check for required files
        required_files = ["_headers", "_redirects", "netlify.toml"]
        for file_name in required_files:
            file_path = self.repo_root / file_name
            if not file_path.exists():
                errors.append(f"Missing required file: {file_name}")
            elif file_path.stat().st_size == 0:
                errors.append(f"Empty file: {file_name}")
        
        return len(errors) == 0, errors
    
    def _check_build_config(self) -> tuple[bool, list]:
        """Check build configuration"""
        errors = []
        
        # Check for package.json in frontend
        frontend_dirs = ["bridge-frontend", "frontend", "apps/web"]
        has_frontend = False
        
        for dir_name in frontend_dirs:
            pkg_json = self.repo_root / dir_name / "package.json"
            if pkg_json.exists():
                has_frontend = True
                # Could validate package.json structure here
                break
        
        if not has_frontend:
            errors.append("No frontend package.json found")
        
        # Check for Python requirements
        if not (self.repo_root / "requirements.txt").exists():
            errors.append("Missing requirements.txt")
        
        return len(errors) == 0, errors
    
    def _check_routes(self) -> tuple[bool, list]:
        """Check route configuration"""
        errors = []
        
        # Simple check: verify _redirects has API routes
        redirects_file = self.repo_root / "_redirects"
        if redirects_file.exists():
            content = redirects_file.read_text()
            if "/api/*" not in content:
                errors.append("Missing API route in _redirects")
            if "/.netlify/functions/server" not in content and "/api/*" in content:
                errors.append("API route not pointing to serverless function")
        
        return len(errors) == 0, errors
    
    def run_virtual_netlify(self) -> SimulationReport:
        """
        Run virtual Netlify deployment simulation
        
        Returns:
            SimulationReport with validation results
        """
        if not self.enabled:
            logger.info("🧭 Sanctum: Disabled, skipping simulation")
            return SimulationReport()
        
        logger.info("🧭 Sanctum: Running virtual Netlify simulation...")
        
        # Perform checks
        config_ok, config_errors = self._check_netlify_config()
        build_ok, build_errors = self._check_build_config()
        routes_ok, route_errors = self._check_routes()
        
        all_errors = config_errors + build_errors + route_errors
        
        report = SimulationReport(
            can_build=build_ok and config_ok,
            routes_ok=routes_ok,
            config_ok=config_ok,
            errors=all_errors
        )
        
        if report.has_errors():
            logger.warning(f"⚠️ Sanctum: Detected {len(all_errors)} issue(s)")
            for error in all_errors:
                logger.warning(f"  - {error}")
        else:
            logger.info("✅ Sanctum: Simulation passed")
        
        return report
    
    async def run_predeploy_check(self) -> SimulationReport:
        """
        Main entry point - runs predictive deployment check
        
        Integrates with:
        - Genesis Bus: publishes sanctum.predeploy.success/failure
        - Cascade: orchestrates auto_heal on failure
        - Forge: triggers repair on configuration issues
        - Truth: certifies successful simulation
        
        Returns:
            SimulationReport with validation results
        """
        logger.info("🧭 Sanctum: Running predictive deployment simulation...")
        
        sim_report = self.run_virtual_netlify()
        
        # Import engines dynamically to avoid circular dependencies
        try:
            from bridge_backend.genesis.bus import genesis_bus
            from bridge_backend.engines.chimera.adapters.truth_adapter import TruthGate
            
            if sim_report.has_errors():
                logger.warning("⚠️ Sanctum detected issues — triggering Forge repair.")
                
                # Publish failure event
                await genesis_bus.publish("sanctum.predeploy.failure", sim_report.to_dict())
                
                # Trigger Forge repair if available
                try:
                    from bridge_backend.engines.forge.core import run_full_repair
                    run_full_repair(scan_only=False)
                except ImportError:
                    logger.warning("Forge engine not available for auto-repair")
            else:
                # Certify with Truth Engine
                truth = TruthGate()
                cert_result = await truth.certify(
                    sim_report.to_dict(),
                    {"ok": True}
                )
                
                if cert_result.get("certified"):
                    logger.info("✅ Sanctum: Truth certified predeploy pass")
                
                # Publish success event
                await genesis_bus.publish("sanctum.predeploy.success", sim_report.to_dict())
        
        except Exception as e:
            logger.error(f"❌ Sanctum: Error during integration: {e}")
        
        return sim_report


# CLI entry point for standalone execution
if __name__ == "__main__":
    import asyncio
    
    async def main():
        engine = SanctumEngine()
        report = await engine.run_predeploy_check()
        
        print("\n" + "="*60)
        print("🧭 Sanctum Simulation Report")
        print("="*60)
        print(f"Can Build: {'✅' if report.can_build else '❌'}")
        print(f"Routes OK: {'✅' if report.routes_ok else '❌'}")
        print(f"Config OK: {'✅' if report.config_ok else '❌'}")
        
        if report.errors:
            print("\nErrors detected:")
            for error in report.errors:
                print(f"  - {error}")
        else:
            print("\n✅ All checks passed!")
        
        print("="*60)
        
        # Exit with error code if simulation failed
        exit(1 if report.has_errors() else 0)
    
    asyncio.run(main())
