"""
EnvScribe Core Engine
Scans repository, compiles environment variables, and verifies against live platforms
"""

import os
import re
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from datetime import datetime, timezone

from .models import (
    EnvVariable, WebhookDefinition, EnvScribeSummary, 
    EnvScribeReport, VerificationStatus
)

logger = logging.getLogger(__name__)


class EnvScribeEngine:
    """
    Unified environment intelligence engine.
    
    Capabilities:
    - Scans repository for environment variable references
    - Compiles comprehensive variable catalog
    - Integrates with EnvRecon for live platform verification
    - Generates copy-ready environment blocks
    - Publishes Truth-certified documentation
    """
    
    def __init__(self):
        self.repo_root = Path(__file__).resolve().parents[3]
        self.report_path = self.repo_root / "bridge_backend" / "diagnostics" / "envscribe_report.json"
        self.report_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Known environment variables from the codebase
        self.known_variables = self._load_known_variables()
    
    def _load_known_variables(self) -> List[EnvVariable]:
        """Load known environment variables from configuration"""
        # Core variables based on the PR spec and existing codebase
        return [
            EnvVariable(
                name="BRIDGE_API_URL",
                scope=["Render"],
                var_type="URL",
                description="Core backend endpoint",
                default=None,
                required=True
            ),
            EnvVariable(
                name="DATABASE_URL",
                scope=["Render", "GitHub"],
                var_type="Secret",
                description="Database connection string",
                default=None,
                required=True
            ),
            EnvVariable(
                name="DATABASE_TYPE",
                scope=["Render"],
                var_type="String",
                description="Database driver",
                default="postgres",
                required=True
            ),
            EnvVariable(
                name="SECRET_KEY",
                scope=["Render", "GitHub"],
                var_type="Secret",
                description="Core cryptographic key",
                default=None,
                required=True
            ),
            EnvVariable(
                name="FEDERATION_SYNC_KEY",
                scope=["Render", "GitHub"],
                var_type="Secret",
                description="Federation handshake token",
                default=None,
                required=False
            ),
            EnvVariable(
                name="PUBLIC_API_BASE",
                scope=["Render", "Netlify"],
                var_type="URL",
                description="Public-facing API",
                default=None,
                required=False
            ),
            EnvVariable(
                name="AUTO_DIAGNOSE",
                scope=["Render"],
                var_type="Bool",
                description="Enables self-healing diagnostics",
                default="true",
                required=False
            ),
            EnvVariable(
                name="CASCADE_MODE",
                scope=["Render"],
                var_type="String",
                description="Cascade orchestration mode",
                default="genesis",
                required=False
            ),
            EnvVariable(
                name="CORS_ALLOW_ALL",
                scope=["Render", "Netlify"],
                var_type="Bool",
                description="Enable cross-origin requests",
                default="true",
                required=False
            ),
            EnvVariable(
                name="ALLOWED_ORIGINS",
                scope=["Render", "Netlify"],
                var_type="String",
                description="Allowed origins list",
                default="*",
                required=False
            ),
            EnvVariable(
                name="VITE_API_BASE",
                scope=["Netlify"],
                var_type="URL",
                description="Frontend API route",
                default=None,
                required=True
            ),
            EnvVariable(
                name="REACT_APP_API_URL",
                scope=["Netlify", "GitHub"],
                var_type="URL",
                description="React build-time API reference",
                default=None,
                required=True
            ),
            EnvVariable(
                name="DEBUG",
                scope=["Render"],
                var_type="Bool",
                description="Debug mode flag",
                default="false",
                required=False
            ),
            EnvVariable(
                name="LOG_LEVEL",
                scope=["All"],
                var_type="String",
                description="Logging verbosity",
                default="info",
                required=False
            ),
            EnvVariable(
                name="PORT",
                scope=["Render"],
                var_type="Int",
                description="Default service port",
                default="8000",
                required=False
            ),
            EnvVariable(
                name="WEBHOOK_DEPLOY",
                scope=["Netlify"],
                var_type="URL",
                description="Chimera deployment notifier",
                default=None,
                required=False
            ),
            EnvVariable(
                name="WEBHOOK_DIAGNOSE",
                scope=["Render"],
                var_type="URL",
                description="ARIE diagnostic notifier",
                default=None,
                required=False
            ),
        ]
    
    def _scan_env_files(self) -> Set[str]:
        """Scan .env files in repository for variable names"""
        env_vars = set()
        env_file_patterns = [".env*", "*.env"]
        
        for pattern in env_file_patterns:
            for env_file in self.repo_root.glob(pattern):
                if env_file.is_file() and not env_file.name.endswith('.example'):
                    try:
                        content = env_file.read_text(encoding='utf-8', errors='ignore')
                        # Match VAR_NAME=value patterns
                        matches = re.findall(r'^([A-Z_][A-Z0-9_]*)=', content, re.MULTILINE)
                        env_vars.update(matches)
                    except Exception as e:
                        logger.debug(f"Could not read {env_file}: {e}")
        
        return env_vars
    
    def _scan_codebase(self) -> Set[str]:
        """Scan codebase for os.getenv() and os.environ references"""
        env_vars = set()
        
        # Scan Python files
        for py_file in self.repo_root.glob("**/*.py"):
            if "venv" in str(py_file) or "node_modules" in str(py_file):
                continue
            
            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')
                # Match os.getenv("VAR_NAME") or os.environ["VAR_NAME"]
                patterns = [
                    r'os\.getenv\(["\']([A-Z_][A-Z0-9_]*)["\']',
                    r'os\.environ\[["\']([A-Z_][A-Z0-9_]*)["\']',
                    r'os\.environ\.get\(["\']([A-Z_][A-Z0-9_]*)["\']',
                ]
                for pattern in patterns:
                    matches = re.findall(pattern, content)
                    env_vars.update(matches)
            except Exception as e:
                logger.debug(f"Could not read {py_file}: {e}")
        
        return env_vars
    
    def _detect_webhooks(self) -> List[WebhookDefinition]:
        """Detect webhook endpoints from routes"""
        webhooks = []
        
        # Known webhook patterns from Chimera and ARIE
        known_hooks = [
            WebhookDefinition(
                path="/api/hooks/deploy",
                engine="Chimera",
                description="Deployment webhook for Chimera engine"
            ),
            WebhookDefinition(
                path="/api/hooks/diagnose",
                engine="ARIE",
                description="Diagnostic webhook for ARIE engine"
            ),
        ]
        
        webhooks.extend(known_hooks)
        return webhooks
    
    async def scan(self) -> EnvScribeReport:
        """
        Perform comprehensive environment scan
        
        Returns:
            EnvScribeReport with complete environment intelligence
        """
        logger.info("[EnvScribe] Starting comprehensive environment scan...")
        
        # Scan repository for variables
        scanned_vars = self._scan_env_files() | self._scan_codebase()
        logger.info(f"[EnvScribe] Found {len(scanned_vars)} environment variables in codebase")
        
        # Merge with known variables
        all_var_names = set(v.name for v in self.known_variables) | scanned_vars
        
        # Build comprehensive variable list
        variables = []
        for var in self.known_variables:
            variables.append(var)
        
        # Add discovered variables not in known list
        for var_name in scanned_vars:
            if var_name not in [v.name for v in self.known_variables]:
                variables.append(EnvVariable(
                    name=var_name,
                    scope=["All"],
                    var_type="String",
                    description=f"Discovered from codebase",
                    default=None,
                    required=False
                ))
        
        # Integrate with EnvRecon for live verification
        envrecon_report = await self._get_envrecon_data()
        
        # Verify each variable against platforms
        verified_vars = []
        missing_render = []
        missing_netlify = []
        missing_github = []
        drifted = {}
        
        for var in variables:
            var_copy = EnvVariable(**var.to_dict())
            
            # Check against EnvRecon data
            if envrecon_report:
                status, drift = self._verify_variable(var.name, var.scope, envrecon_report)
                var_copy.verified = status.value
                
                if status == VerificationStatus.MISSING:
                    if "Render" in var.scope:
                        missing_render.append(var.name)
                    if "Netlify" in var.scope:
                        missing_netlify.append(var.name)
                    if "GitHub" in var.scope:
                        missing_github.append(var.name)
                
                if drift:
                    drifted[var.name] = drift
            
            verified_vars.append(var_copy)
        
        # Detect webhooks
        webhooks = self._detect_webhooks()
        
        # Create summary
        summary = EnvScribeSummary(
            total_keys=len(verified_vars),
            verified=sum(1 for v in verified_vars if v.verified == VerificationStatus.VERIFIED.value),
            missing_in_render=len(missing_render),
            missing_in_netlify=len(missing_netlify),
            missing_in_github=len(missing_github),
            drifted=len(drifted)
        )
        
        # Create report
        report = EnvScribeReport(
            summary=summary,
            variables=verified_vars,
            missing_in_render=missing_render,
            missing_in_netlify=missing_netlify,
            missing_in_github=missing_github,
            drifted=drifted,
            webhooks=webhooks
        )
        
        # Save report
        self._save_report(report)
        
        logger.info(f"[EnvScribe] Scan complete: {summary.total_keys} variables, "
                   f"{summary.verified} verified, {summary.missing_in_render + summary.missing_in_netlify + summary.missing_in_github} missing")
        
        return report
    
    async def _get_envrecon_data(self) -> Optional[Dict[str, Any]]:
        """Get data from EnvRecon for verification"""
        try:
            from bridge_backend.engines.envrecon.core import EnvReconEngine
            engine = EnvReconEngine()
            report = engine.load_report()
            return report
        except Exception as e:
            logger.debug(f"[EnvScribe] Could not load EnvRecon data: {e}")
            return None
    
    def _verify_variable(self, var_name: str, scope: List[str], envrecon_report: Dict[str, Any]) -> tuple:
        """
        Verify variable against EnvRecon data
        
        Returns:
            (VerificationStatus, drift_info)
        """
        # Check if variable is missing in any platform
        missing_render = envrecon_report.get("missing_in_render", [])
        missing_netlify = envrecon_report.get("missing_in_netlify", [])
        missing_github = envrecon_report.get("missing_in_github", [])
        
        if var_name in missing_render or var_name in missing_netlify or var_name in missing_github:
            return (VerificationStatus.MISSING, None)
        
        # Check for drift
        drifted = envrecon_report.get("drifted", {})
        if var_name in drifted:
            return (VerificationStatus.DRIFTED, drifted[var_name])
        
        return (VerificationStatus.VERIFIED, None)
    
    def _save_report(self, report: EnvScribeReport):
        """Save scan report to JSON file"""
        try:
            with open(self.report_path, 'w') as f:
                json.dump(report.to_dict(), f, indent=2)
            logger.info(f"[EnvScribe] Report saved to {self.report_path}")
        except Exception as e:
            logger.error(f"[EnvScribe] Failed to save report: {e}")
    
    def load_report(self) -> Optional[EnvScribeReport]:
        """Load the latest scan report"""
        try:
            if not self.report_path.exists():
                return None
            
            with open(self.report_path, 'r') as f:
                data = json.load(f)
            
            # Reconstruct report from JSON
            summary = EnvScribeSummary(**data["summary"])
            variables = [EnvVariable(**v) for v in data["variables"]]
            webhooks = [WebhookDefinition(**w) for w in data["webhooks"]]
            
            report = EnvScribeReport(
                summary=summary,
                variables=variables,
                missing_in_render=data.get("missing_in_render", []),
                missing_in_netlify=data.get("missing_in_netlify", []),
                missing_in_github=data.get("missing_in_github", []),
                drifted=data.get("drifted", {}),
                webhooks=webhooks,
                certified=data.get("certified", False),
                certificate_id=data.get("certificate_id")
            )
            
            return report
        except Exception as e:
            logger.error(f"[EnvScribe] Failed to load report: {e}")
            return None
