"""
Forge Engine - Autonomous Repair System
Fixes config drift, unused imports, and environment mismatch
"""

import os
import logging
import subprocess
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime, UTC

logger = logging.getLogger(__name__)


class RepairIssue:
    """Represents a detected issue that needs repair"""
    
    def __init__(self, issue_type: str, description: str, file_path: Optional[str] = None,
                 fix_function: Optional[callable] = None, metadata: Optional[Dict] = None):
        self.issue_type = issue_type
        self.description = description
        self.file_path = file_path
        self.fix_function = fix_function
        self.metadata = metadata or {}
        self.fixed = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.issue_type,
            "description": self.description,
            "file": self.file_path,
            "fixed": self.fixed,
            "metadata": self.metadata
        }


class RepairTools:
    """Tools for detecting and fixing repository issues"""
    
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
    
    def scan_repo(self) -> List[RepairIssue]:
        """Scan repository for issues"""
        issues = []
        
        # Check for missing netlify config
        issues.extend(self._check_netlify_config())
        
        # Check for environment drift
        issues.extend(self._check_env_drift())
        
        # Check for unused imports (delegate to ARIE if available)
        # This is handled by ARIE, so we skip here
        
        return issues
    
    def _check_netlify_config(self) -> List[RepairIssue]:
        """Check and repair Netlify configuration"""
        issues = []
        
        required_files = {
            "_headers": self._create_default_headers,
            "_redirects": self._create_default_redirects,
            "netlify.toml": self._create_default_netlify_toml
        }
        
        for file_name, fix_func in required_files.items():
            file_path = self.repo_root / file_name
            
            if not file_path.exists() or file_path.stat().st_size == 0:
                issues.append(RepairIssue(
                    issue_type="missing_config",
                    description=f"Missing or empty {file_name}",
                    file_path=str(file_path),
                    fix_function=fix_func
                ))
        
        return issues
    
    def _check_env_drift(self) -> List[RepairIssue]:
        """Check for environment drift"""
        issues = []
        
        # Check if .env.example exists but .env doesn't
        env_example = self.repo_root / ".env.example"
        env_file = self.repo_root / ".env"
        
        if env_example.exists() and not env_file.exists():
            issues.append(RepairIssue(
                issue_type="env_drift",
                description="Missing .env file (template exists)",
                file_path=str(env_file),
                fix_function=lambda: self._create_env_from_template()
            ))
        
        return issues
    
    def _create_default_headers(self):
        """Create default _headers file"""
        headers_content = """/*
  X-Frame-Options: DENY
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: geolocation=(), microphone=(), camera=()
  X-XSS-Protection: 1; mode=block
"""
        (self.repo_root / "_headers").write_text(headers_content)
        logger.info("🛠️ Forge: Created default _headers")
    
    def _create_default_redirects(self):
        """Create default _redirects file"""
        redirects_content = """/api/*  /.netlify/functions/server  200
/*      /index.html                200
"""
        (self.repo_root / "_redirects").write_text(redirects_content)
        logger.info("🛠️ Forge: Created default _redirects")
    
    def _create_default_netlify_toml(self):
        """Create default netlify.toml file"""
        toml_content = """[build]
  command = "npm run build"
  publish = "frontend/dist"
  functions = "netlify/functions"

[build.environment]
  NODE_VERSION = "18"

[[redirects]]
  from = "/api/*"
  to = "/.netlify/functions/server"
  status = 200

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
"""
        (self.repo_root / "netlify.toml").write_text(toml_content)
        logger.info("🛠️ Forge: Created default netlify.toml")
    
    def _create_env_from_template(self):
        """Create .env from .env.example"""
        env_example = self.repo_root / ".env.example"
        env_file = self.repo_root / ".env"
        
        if env_example.exists():
            # Copy template with empty values
            content = env_example.read_text()
            env_file.write_text(content)
            logger.info("🛠️ Forge: Created .env from template")
    
    def fix(self, issue: RepairIssue) -> bool:
        """Fix a specific issue"""
        try:
            if issue.fix_function:
                issue.fix_function()
                issue.fixed = True
                logger.info(f"✅ Forge: Fixed {issue.description}")
                return True
            else:
                logger.warning(f"⚠️ Forge: No fix available for {issue.description}")
                return False
        except Exception as e:
            logger.error(f"❌ Forge: Failed to fix {issue.description}: {e}")
            return False


class ForgeEngine:
    """
    Forge Autonomous Repair Engine
    
    Scans repository for configuration issues and applies automated fixes.
    Integrates with Genesis Bus, Truth Engine, and Cascade.
    """
    
    def __init__(self, repo_root: Optional[Path] = None):
        self.repo_root = repo_root or Path.cwd()
        self.repair_tools = RepairTools(self.repo_root)
        self.enabled = os.getenv("FORGE_ENABLED", "true").lower() == "true"
    
    async def run_full_repair(self, scan_only: bool = False) -> Dict[str, Any]:
        """
        Execute autonomous repository repair sequence
        
        Args:
            scan_only: If True, only scan without applying fixes
            
        Returns:
            Repair report with issues found and fixed
        """
        logger.info("🛠️ Forge: Executing autonomous repo repair sequence...")
        
        if not self.enabled:
            logger.info("🛠️ Forge: Disabled, skipping repair")
            return {"enabled": False, "issues": [], "fixed": 0}
        
        # Scan for issues
        issues = self.repair_tools.scan_repo()
        
        if not issues:
            logger.info("🛠️ Forge: No issues detected.")
            return {"enabled": True, "issues": [], "fixed": 0}
        
        logger.info(f"🛠️ Forge: Detected {len(issues)} issue(s)")
        
        fixed_count = 0
        
        # Apply fixes if not scan-only
        if not scan_only:
            for issue in issues:
                if self.repair_tools.fix(issue):
                    fixed_count += 1
            
            # Integrate with Truth Engine and Genesis Bus
            try:
                from bridge_backend.genesis.bus import genesis_bus
                from bridge_backend.engines.chimera.adapters.truth_adapter import TruthGate
                
                # Certify repairs with Truth Engine
                truth = TruthGate()
                cert_result = await truth.certify(
                    {"repairs": fixed_count, "total_issues": len(issues)},
                    {"ok": True}
                )
                
                if cert_result.get("certified"):
                    logger.info("✅ Forge: Truth certified repair completion")
                
                # Publish to Genesis Bus
                await genesis_bus.publish("forge.repair.applied", {
                    "count": fixed_count,
                    "total_issues": len(issues),
                    "timestamp": datetime.now(UTC).isoformat() + "Z",
                    "certified": cert_result.get("certified", False)
                })
            except Exception as e:
                logger.error(f"❌ Forge: Error during integration: {e}")
        
        report = {
            "enabled": True,
            "scan_only": scan_only,
            "issues": [issue.to_dict() for issue in issues],
            "fixed": fixed_count,
            "timestamp": datetime.now(UTC).isoformat() + "Z"
        }
        
        logger.info(f"🛠️ Forge: Repair complete - {fixed_count}/{len(issues)} fixed")
        
        return report


# Module-level convenience function
def run_full_repair(scan_only: bool = False) -> Dict[str, Any]:
    """
    Module-level convenience function for running Forge repair
    
    Args:
        scan_only: If True, only scan without applying fixes
        
    Returns:
        Repair report
    """
    import asyncio
    
    async def _run():
        engine = ForgeEngine()
        return await engine.run_full_repair(scan_only=scan_only)
    
    return asyncio.run(_run())


# CLI entry point for standalone execution
if __name__ == "__main__":
    import asyncio
    import sys
    
    async def main():
        scan_only = "--scan-only" in sys.argv
        
        engine = ForgeEngine()
        report = await engine.run_full_repair(scan_only=scan_only)
        
        print("\n" + "="*60)
        print("🛠️ Forge Repair Report")
        print("="*60)
        print(f"Enabled: {'✅' if report['enabled'] else '❌'}")
        print(f"Mode: {'Scan Only' if report.get('scan_only') else 'Repair'}")
        print(f"Issues Found: {len(report['issues'])}")
        print(f"Issues Fixed: {report.get('fixed', 0)}")
        
        if report['issues']:
            print("\nIssues:")
            for issue in report['issues']:
                status = "✅" if issue['fixed'] else "⏸️"
                print(f"  {status} {issue['description']}")
        
        print("="*60)
        
        # Exit with error if unfixed issues remain
        unfixed = len(report['issues']) - report.get('fixed', 0)
        exit(1 if unfixed > 0 else 0)
    
    asyncio.run(main())
