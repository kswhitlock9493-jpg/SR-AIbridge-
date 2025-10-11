"""
EnvRecon Core Engine
Autonomous environment reconciliation across Render, Netlify, GitHub, and local configurations
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
from dotenv import dotenv_values
import httpx

logger = logging.getLogger(__name__)


class EnvReconEngine:
    """
    Cross-platform environment reconciliation engine.
    Audits and normalizes variables across .env files, Render, Netlify, and GitHub.
    """
    
    def __init__(self):
        self.report_path = Path(__file__).parent.parent.parent / "logs" / "env_recon_report.json"
        self.report_path.parent.mkdir(parents=True, exist_ok=True)
        
    async def fetch_render_env(self) -> Dict[str, str]:
        """Fetch environment variables from Render API"""
        api_key = os.getenv("RENDER_API_KEY")
        service_id = os.getenv("RENDER_SERVICE_ID")
        
        if not api_key or not service_id:
            logger.warning("⚠️ Render credentials not configured")
            return {}
        
        url = f"https://api.render.com/v1/services/{service_id}/env-vars"
        headers = {"Authorization": f"Bearer {api_key}"}
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(url, headers=headers)
                resp.raise_for_status()
                data = resp.json()
                return {item["key"]: item["value"] for item in data}
        except Exception as e:
            logger.error(f"❌ Failed to fetch Render env: {e}")
            return {}
    
    async def fetch_netlify_env(self) -> Dict[str, str]:
        """Fetch environment variables from Netlify API"""
        auth_token = os.getenv("NETLIFY_AUTH_TOKEN")
        site_id = os.getenv("NETLIFY_SITE_ID")
        
        if not auth_token or not site_id:
            logger.warning("⚠️ Netlify credentials not configured")
            return {}
        
        url = f"https://api.netlify.com/api/v1/sites/{site_id}/env"
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(url, headers=headers)
                resp.raise_for_status()
                data = resp.json()
                return {item["key"]: item["value"] for item in data}
        except Exception as e:
            logger.error(f"❌ Failed to fetch Netlify env: {e}")
            return {}
    
    async def fetch_github_secrets(self) -> Dict[str, str]:
        """
        Fetch GitHub secrets (note: values are not directly accessible via API).
        This returns a list of secret names only.
        """
        github_token = os.getenv("GITHUB_TOKEN")
        github_repo = os.getenv("GITHUB_REPO")
        
        if not github_token or not github_repo:
            logger.warning("⚠️ GitHub credentials not configured")
            return {}
        
        url = f"https://api.github.com/repos/{github_repo}/actions/secrets"
        headers = {
            "Authorization": f"Bearer {github_token}",
            "Accept": "application/vnd.github+json"
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(url, headers=headers)
                resp.raise_for_status()
                data = resp.json()
                # GitHub API only returns secret names, not values
                return {secret["name"]: "<secret>" for secret in data.get("secrets", [])}
        except Exception as e:
            logger.error(f"❌ Failed to fetch GitHub secrets: {e}")
            return {}
    
    def load_local_env(self) -> Dict[str, str]:
        """Load environment variables from local .env files"""
        env_files = [".env", ".env.production", ".env.local"]
        combined = {}
        
        base_path = Path(__file__).parent.parent.parent.parent
        
        for env_file in env_files:
            file_path = base_path / env_file
            if file_path.exists():
                try:
                    env_vars = dotenv_values(str(file_path))
                    combined.update(env_vars)
                    logger.info(f"✅ Loaded {len(env_vars)} vars from {env_file}")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to load {env_file}: {e}")
        
        return combined
    
    async def reconcile(self) -> Dict[str, Any]:
        """
        Perform full environment reconciliation across all platforms.
        Returns a comprehensive diff report.
        """
        logger.info("🔍 Starting EnvRecon audit...")
        
        # Fetch from all sources
        local = self.load_local_env()
        render = await self.fetch_render_env()
        netlify = await self.fetch_netlify_env()
        github = await self.fetch_github_secrets()
        
        # Get all unique keys
        all_keys = set(local.keys()) | set(render.keys()) | set(netlify.keys()) | set(github.keys())
        
        # Categorize variables
        missing_in_render = [k for k in all_keys if k in local and k not in render]
        missing_in_netlify = [k for k in all_keys if k in local and k not in netlify]
        missing_in_github = [k for k in all_keys if k in local and k not in github]
        
        extra_in_render = [k for k in render if k not in local]
        extra_in_netlify = [k for k in netlify if k not in local]
        
        # Detect conflicts (same key, different values)
        conflicts = {}
        for key in all_keys:
            values = {}
            if key in render:
                values["render"] = render[key]
            if key in netlify:
                values["netlify"] = netlify[key]
            if key in github:
                values["github"] = github[key]
            if key in local:
                values["local"] = local[key]
            
            # Check if values differ (excluding GitHub secrets which are masked)
            unique_values = set(v for k, v in values.items() if k != "github" and v != "<secret>")
            if len(unique_values) > 1:
                conflicts[key] = values
        
        report = {
            "missing_in_render": missing_in_render,
            "missing_in_netlify": missing_in_netlify,
            "missing_in_github": missing_in_github,
            "extra_in_render": extra_in_render,
            "extra_in_netlify": extra_in_netlify,
            "conflicts": conflicts,
            "autofixed": [],  # Populated by auto-heal
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "summary": {
                "total_keys": len(all_keys),
                "local_count": len(local),
                "render_count": len(render),
                "netlify_count": len(netlify),
                "github_count": len(github),
            }
        }
        
        # Save report
        self.save_report(report)
        
        logger.info(f"✅ EnvRecon audit complete - {len(all_keys)} total variables analyzed")
        
        # Notify Autonomy engine via adapter
        try:
            from bridge_backend.bridge_core.engines.adapters.envrecon_autonomy_link import envrecon_autonomy_link
            await envrecon_autonomy_link.notify_reconciliation_complete(report)
            await envrecon_autonomy_link.notify_drift_detected(report)
        except Exception as e:
            logger.debug(f"EnvRecon-Autonomy link notification skipped: {e}")
        
        return report
    
    def save_report(self, report: Dict[str, Any]):
        """Save reconciliation report to JSON file"""
        try:
            with open(self.report_path, 'w') as f:
                json.dump(report, f, indent=2)
            logger.info(f"📄 Report saved to {self.report_path}")
        except Exception as e:
            logger.error(f"❌ Failed to save report: {e}")
    
    def load_report(self) -> Optional[Dict[str, Any]]:
        """Load the latest reconciliation report"""
        if not self.report_path.exists():
            return None
        
        try:
            with open(self.report_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"❌ Failed to load report: {e}")
            return None
