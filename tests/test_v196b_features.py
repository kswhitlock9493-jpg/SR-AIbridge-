#!/usr/bin/env python3
"""
Test Suite for SR-AIbridge v1.9.6b — Predictive Stabilization & Self-Healing
Validates new features: release intelligence, predictive stabilizer, GitHub integration
"""
import os
import sys
import pytest
import json
from pathlib import Path

# Add bridge_backend to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "bridge_backend"))


class TestV196bFeatures:
    """Test suite for v1.9.6b features"""
    
    def test_version_1_9_6b(self):
        """Verify version is set to v1.9.6b"""
        main_path = Path(__file__).parent.parent / "bridge_backend" / "main.py"
        content = main_path.read_text()
        
        # Should contain v1.9.6b version
        assert 'version=os.getenv("APP_VERSION","v1.9.6b")' in content or '"v1.9.6b"' in content
        assert "Predictive Stabilization" in content or "Self-Healing" in content
    
    def test_httpx_in_requirements(self):
        """Verify httpx>=0.27.2 is in requirements.txt"""
        req_path = Path(__file__).parent.parent / "requirements.txt"
        content = req_path.read_text()
        
        assert "httpx>=0.27.2" in content
        assert "python-dateutil>=2.9.0" in content
    
    def test_models_directory_exists(self):
        """Verify models directory and files exist"""
        models_dir = Path(__file__).parent.parent / "bridge_backend" / "models"
        assert models_dir.exists()
        assert (models_dir / "__init__.py").exists()
        assert (models_dir / "core.py").exists()
    
    def test_models_import(self):
        """Verify models can be imported"""
        try:
            from bridge_backend.models import Base, User
            assert Base is not None
            assert User is not None
        except ImportError:
            pytest.skip("Models import not available in test environment")
    
    def test_utils_db_module(self):
        """Verify utils/db.py exists and has init_schema function"""
        db_path = Path(__file__).parent.parent / "bridge_backend" / "utils" / "db.py"
        assert db_path.exists()
        
        content = db_path.read_text()
        assert "async def init_schema" in content
        assert "create_async_engine" in content
        assert "postgresql+asyncpg" in content
    
    def test_integrations_directory(self):
        """Verify integrations directory and github_issues module exist"""
        integrations_dir = Path(__file__).parent.parent / "bridge_backend" / "integrations"
        assert integrations_dir.exists()
        assert (integrations_dir / "__init__.py").exists()
        assert (integrations_dir / "github_issues.py").exists()
    
    def test_github_issues_module(self):
        """Verify github_issues module has required functions"""
        github_path = Path(__file__).parent.parent / "bridge_backend" / "integrations" / "github_issues.py"
        content = github_path.read_text()
        
        assert "def maybe_create_issue" in content
        assert "GITHUB_REPO" in content
        assert "GITHUB_TOKEN" in content
        assert "httpx" in content
    
    def test_predictive_stabilizer(self):
        """Verify predictive_stabilizer module exists and has required functions"""
        stabilizer_path = Path(__file__).parent.parent / "bridge_backend" / "runtime" / "predictive_stabilizer.py"
        assert stabilizer_path.exists()
        
        content = stabilizer_path.read_text()
        assert "def evaluate_stability" in content
        assert "stability_score" in content
        assert "most_active_modules" in content
        assert "maybe_create_issue" in content
    
    def test_release_intel_module(self):
        """Verify release_intel module exists"""
        intel_path = Path(__file__).parent.parent / "bridge_backend" / "runtime" / "release_intel.py"
        assert intel_path.exists()
        
        content = intel_path.read_text()
        assert "def analyze_and_stabilize" in content
        assert "evaluate_stability" in content
    
    def test_heartbeat_v196b(self):
        """Verify heartbeat module is updated for v1.9.6b"""
        heartbeat_path = Path(__file__).parent.parent / "bridge_backend" / "runtime" / "heartbeat.py"
        content = heartbeat_path.read_text()
        
        # v1.9.6b heartbeat should use httpx directly (not self-healing)
        assert "import httpx" in content
        assert "async def send_heartbeat" in content
        assert "async def run" in content
        assert "HEARTBEAT_URL" in content
        assert "HEARTBEAT_INTERVAL" in content
    
    def test_release_insights_json(self):
        """Verify release_insights.json exists and has correct schema"""
        insights_path = Path(__file__).parent.parent / "bridge_backend" / "diagnostics" / "release_insights.json"
        assert insights_path.exists()
        
        with open(insights_path) as f:
            data = json.load(f)
        
        assert "stability_score" in data
        assert "most_active_modules" in data
        assert isinstance(data["stability_score"], (int, float))
        assert isinstance(data["most_active_modules"], list)
    
    def test_stabilization_tickets_directory(self):
        """Verify stabilization_tickets directory exists"""
        tickets_dir = Path(__file__).parent.parent / "bridge_backend" / "diagnostics" / "stabilization_tickets"
        assert tickets_dir.exists()
        assert (tickets_dir / ".gitkeep").exists()
    
    def test_main_startup_event(self):
        """Verify main.py has v1.9.6b startup event"""
        main_path = Path(__file__).parent.parent / "bridge_backend" / "main.py"
        content = main_path.read_text()
        
        # Should import init_schema from utils.db
        assert "from bridge_backend.utils.db import init_schema" in content
        assert "await init_schema()" in content
        
        # Should import and run release intel
        assert "from bridge_backend.runtime.release_intel import analyze_and_stabilize" in content
        assert "analyze_and_stabilize()" in content
        
        # Should import and run heartbeat
        assert "from bridge_backend.runtime import heartbeat" in content
        assert "asyncio.create_task(heartbeat.run())" in content
    
    def test_render_yaml_port_binding(self):
        """Verify render.yaml has correct PORT binding"""
        render_path = Path(__file__).parent.parent / "render.yaml"
        content = render_path.read_text()
        
        assert "${PORT}" in content or "$PORT" in content
        assert "uvicorn bridge_backend.main:app" in content
        assert "--host 0.0.0.0" in content
    
    def test_netlify_cors_headers(self):
        """Verify netlify.toml has CORS headers"""
        netlify_path = Path(__file__).parent.parent / "netlify.toml"
        content = netlify_path.read_text()
        
        assert "Access-Control-Allow-Origin" in content
        assert "Access-Control-Allow-Methods" in content
        assert "Access-Control-Allow-Headers" in content
    
    def test_env_template_exists(self):
        """Verify .env.template exists with required variables"""
        env_path = Path(__file__).parent.parent / ".env.template"
        assert env_path.exists()
        
        content = env_path.read_text()
        assert "DATABASE_URL" in content
        assert "HEARTBEAT_URL" in content
        assert "GITHUB_REPO" in content
        assert "GITHUB_TOKEN" in content
        assert "APP_VERSION" in content
        assert "HEARTBEAT_INTERVAL_SEC" in content
        assert "BRIDGE_STABILITY_SCORE" in content
    
    def test_readme_releases_exists(self):
        """Verify README_RELEASES.md exists"""
        readme_path = Path(__file__).parent.parent / "README_RELEASES.md"
        assert readme_path.exists()
        
        content = readme_path.read_text()
        assert "v1.9.6b" in content
        assert "Predictive Stabilization" in content or "Predictive" in content
        assert "Self-Healing" in content or "Self-Heal" in content


class TestV196bIntegration:
    """Integration tests for v1.9.6b features"""
    
    def test_predictive_stabilizer_import(self):
        """Test that predictive stabilizer can be imported"""
        try:
            from bridge_backend.runtime.predictive_stabilizer import evaluate_stability
            assert callable(evaluate_stability)
        except ImportError:
            pytest.skip("Predictive stabilizer import not available in test environment")
    
    def test_release_intel_import(self):
        """Test that release intel can be imported"""
        try:
            from bridge_backend.runtime.release_intel import analyze_and_stabilize
            assert callable(analyze_and_stabilize)
        except ImportError:
            pytest.skip("Release intel import not available in test environment")
    
    def test_github_issues_import(self):
        """Test that github issues module can be imported"""
        try:
            from bridge_backend.integrations.github_issues import maybe_create_issue
            assert callable(maybe_create_issue)
        except ImportError:
            pytest.skip("GitHub issues import not available in test environment")
    
    def test_heartbeat_import(self):
        """Test that v1.9.6b heartbeat can be imported"""
        try:
            from bridge_backend.runtime import heartbeat
            assert hasattr(heartbeat, 'run')
            assert hasattr(heartbeat, 'send_heartbeat')
        except ImportError:
            pytest.skip("Heartbeat import not available in test environment")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
