#!/usr/bin/env python3
"""
Tests for Sovereign Audit & Repair Orchestrator
"""

import os
import sys
import json
import pytest
import tempfile
import shutil
import subprocess
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add bridge_backend to path
REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from sovereign_audit_orchestrator import (
    AuditResult,
    AuditReport,
    SovereignGitAuditor,
    SovereignNetlifyAuditor,
    SovereignRepositoryAuditor,
    SovereignAuditOrchestrator
)


class TestAuditResult:
    """Test AuditResult dataclass"""
    
    def test_audit_result_creation(self):
        """Test creating an audit result"""
        result = AuditResult(
            category="test",
            check_name="test_check",
            status="PASS",
            message="Test passed",
            severity="INFO"
        )
        
        assert result.category == "test"
        assert result.check_name == "test_check"
        assert result.status == "PASS"
        assert result.message == "Test passed"
        assert result.severity == "INFO"
        assert result.auto_repair_available is False
        assert result.repaired is False
    
    def test_audit_result_with_details(self):
        """Test audit result with details"""
        result = AuditResult(
            category="test",
            check_name="test_check",
            status="FAIL",
            message="Test failed",
            details={"error": "test error"},
            severity="HIGH",
            auto_repair_available=True
        )
        
        assert result.details == {"error": "test error"}
        assert result.auto_repair_available is True


class TestSovereignGitAuditor:
    """Test Git sovereign auditor"""
    
    @pytest.fixture
    def temp_repo(self):
        """Create a temporary repository"""
        temp_dir = tempfile.mkdtemp()
        repo_path = Path(temp_dir)
        
        # Initialize git repo
        subprocess.run(['git', 'init'], cwd=repo_path, check=True, capture_output=True)
        subprocess.run(['git', 'config', 'user.name', 'Test User'], cwd=repo_path, check=True, capture_output=True)
        subprocess.run(['git', 'config', 'user.email', 'test@example.com'], cwd=repo_path, check=True, capture_output=True)
        
        # Create .gitignore
        gitignore = repo_path / ".gitignore"
        gitignore.write_text("*.env\n__pycache__\nnode_modules\n.DS_Store\n")
        
        # Create git sovereign agent structure
        agent_dir = repo_path / "bridge_backend" / "bridge_core" / "agents" / "git_sovereign"
        agent_dir.mkdir(parents=True, exist_ok=True)
        
        for filename in ["__init__.py", "manifest.py", "autonomy.py", 
                        "sdtf_integration.py", "brh_integration.py", "hxo_integration.py"]:
            (agent_dir / filename).touch()
        
        yield repo_path
        
        # Cleanup
        shutil.rmtree(temp_dir)
    
    def test_git_auditor_initialization(self, temp_repo):
        """Test Git auditor initialization"""
        auditor = SovereignGitAuditor(temp_repo)
        assert auditor.repo_root == temp_repo
        assert auditor.results == []
    
    def test_git_config_check(self, temp_repo):
        """Test Git config checking"""
        auditor = SovereignGitAuditor(temp_repo)
        auditor._check_git_config()
        
        # Should have results for user.name and user.email
        assert len(auditor.results) >= 2
        
        # Check that results contain expected checks
        check_names = [r.check_name for r in auditor.results]
        assert "user.name" in check_names
        assert "user.email" in check_names
    
    def test_git_sovereign_agent_check_pass(self, temp_repo):
        """Test Git sovereign agent check - passing"""
        auditor = SovereignGitAuditor(temp_repo)
        auditor._check_git_sovereign_agent()
        
        # Should pass since we created all required files
        result = auditor.results[0]
        assert result.category == "git_sovereign"
        assert result.status == "PASS"
    
    def test_git_sovereign_agent_check_fail(self, temp_repo):
        """Test Git sovereign agent check - failing"""
        # Remove the agent directory
        agent_dir = temp_repo / "bridge_backend" / "bridge_core" / "agents" / "git_sovereign"
        shutil.rmtree(agent_dir)
        
        auditor = SovereignGitAuditor(temp_repo)
        auditor._check_git_sovereign_agent()
        
        result = auditor.results[0]
        assert result.category == "git_sovereign"
        assert result.status == "FAIL"
    
    def test_gitignore_check_pass(self, temp_repo):
        """Test .gitignore check - passing"""
        auditor = SovereignGitAuditor(temp_repo)
        auditor._check_gitignore()
        
        result = auditor.results[0]
        assert result.category == "git_ignore"
        assert result.status == "PASS"
    
    def test_gitignore_check_missing_patterns(self, temp_repo):
        """Test .gitignore check - missing patterns"""
        # Overwrite .gitignore with incomplete content
        gitignore = temp_repo / ".gitignore"
        gitignore.write_text("*.log\n")
        
        auditor = SovereignGitAuditor(temp_repo)
        auditor._check_gitignore()
        
        result = auditor.results[0]
        assert result.category == "git_ignore"
        assert result.status == "WARNING"
        assert result.auto_repair_available is True
    
    def test_full_audit(self, temp_repo):
        """Test full Git audit"""
        auditor = SovereignGitAuditor(temp_repo)
        results = auditor.audit(auto_repair=False)
        
        # Should have multiple results
        assert len(results) > 0
        
        # Check categories
        categories = set(r.category for r in results)
        assert "git_config" in categories
        assert "git_sovereign" in categories
        assert "git_ignore" in categories


class TestSovereignNetlifyAuditor:
    """Test Netlify sovereign auditor"""
    
    @pytest.fixture
    def temp_repo(self):
        """Create a temporary repository with Netlify files"""
        temp_dir = tempfile.mkdtemp()
        repo_path = Path(temp_dir)
        
        # Create netlify.toml
        netlify_toml = repo_path / "netlify.toml"
        netlify_toml.write_text("""
[build]
  command = "npm run build"
  publish = "dist"

[[headers]]
  for = "/*"
  [headers.values]
    X-Frame-Options = "SAMEORIGIN"
    X-Content-Type-Options = "nosniff"
    Strict-Transport-Security = "max-age=63072000"
""")
        
        # Create .env.netlify
        env_netlify = repo_path / ".env.netlify"
        env_netlify.write_text("FORGE_DOMINION_MODE=sovereign\n")
        
        # Create .env.netlify.example
        env_example = repo_path / ".env.netlify.example"
        env_example.write_text("FORGE_DOMINION_MODE=sovereign\n")
        
        # Create _redirects
        redirects = repo_path / "_redirects"
        redirects.write_text("/api/* https://api.example.com/:splat 200\n")
        
        # Create _headers
        headers = repo_path / "_headers"
        headers.write_text("/*\n  X-Custom-Header: value\n")
        
        # Create netlify functions
        functions_dir = repo_path / "netlify" / "functions"
        functions_dir.mkdir(parents=True, exist_ok=True)
        (functions_dir / "test.js").write_text("exports.handler = async () => {}")
        
        yield repo_path
        
        # Cleanup
        shutil.rmtree(temp_dir)
    
    def test_netlify_auditor_initialization(self, temp_repo):
        """Test Netlify auditor initialization"""
        auditor = SovereignNetlifyAuditor(temp_repo)
        assert auditor.repo_root == temp_repo
        assert auditor.results == []
    
    def test_netlify_toml_check_pass(self, temp_repo):
        """Test netlify.toml check - passing"""
        auditor = SovereignNetlifyAuditor(temp_repo)
        auditor._check_netlify_toml()
        
        # Should have results for toml completeness and security headers
        assert len(auditor.results) >= 2
        
        toml_result = auditor.results[0]
        assert toml_result.category == "netlify_config"
        assert toml_result.status == "PASS"
        
        security_result = auditor.results[1]
        assert security_result.category == "netlify_security"
        assert security_result.status == "PASS"
    
    def test_netlify_toml_missing(self, temp_repo):
        """Test netlify.toml check - missing file"""
        # Remove netlify.toml
        (temp_repo / "netlify.toml").unlink()
        
        auditor = SovereignNetlifyAuditor(temp_repo)
        auditor._check_netlify_toml()
        
        result = auditor.results[0]
        assert result.category == "netlify_config"
        assert result.status == "FAIL"
        assert result.severity == "CRITICAL"
    
    def test_netlify_env_files_check(self, temp_repo):
        """Test Netlify env files check"""
        auditor = SovereignNetlifyAuditor(temp_repo)
        auditor._check_netlify_env_files()
        
        # Should check both .env.netlify and .env.netlify.example
        categories = [r.category for r in auditor.results]
        assert categories.count("netlify_env") >= 2
    
    def test_netlify_functions_check(self, temp_repo):
        """Test Netlify functions check"""
        auditor = SovereignNetlifyAuditor(temp_repo)
        auditor._check_netlify_functions()
        
        result = auditor.results[0]
        assert result.category == "netlify_functions"
        assert result.status == "PASS"
        assert result.details["count"] >= 1
    
    def test_full_audit(self, temp_repo):
        """Test full Netlify audit"""
        auditor = SovereignNetlifyAuditor(temp_repo)
        results = auditor.audit(auto_repair=False)
        
        # Should have multiple results
        assert len(results) > 0
        
        # Check categories
        categories = set(r.category for r in results)
        assert "netlify_config" in categories
        assert "netlify_env" in categories


class TestSovereignRepositoryAuditor:
    """Test repository sovereign auditor"""
    
    @pytest.fixture
    def temp_repo(self):
        """Create a temporary repository with standard structure"""
        temp_dir = tempfile.mkdtemp()
        repo_path = Path(temp_dir)
        
        # Create directory structure
        (repo_path / "bridge_backend").mkdir()
        (repo_path / "bridge-frontend").mkdir()
        (repo_path / "scripts").mkdir()
        (repo_path / "docs").mkdir()
        (repo_path / ".github" / "workflows").mkdir(parents=True)
        
        # Create files
        (repo_path / "README.md").write_text("# Test Repo\n")
        (repo_path / ".gitignore").write_text("*.pyc\n")
        (repo_path / ".env.example").write_text("TEST=value\n")
        (repo_path / "requirements.txt").write_text("pytest\n")
        (repo_path / "bridge_backend" / "pyproject.toml").write_text("[tool.poetry]\n")
        (repo_path / "bridge-frontend" / "package.json").write_text('{"name":"test"}\n')
        (repo_path / "SECURITY.md").write_text("# Security\n")
        (repo_path / ".github" / "workflows" / "test.yml").write_text("name: test\n")
        
        # Create some doc files
        (repo_path / "docs" / "guide.md").write_text("# Guide\n")
        
        yield repo_path
        
        # Cleanup
        shutil.rmtree(temp_dir)
    
    def test_repo_auditor_initialization(self, temp_repo):
        """Test repository auditor initialization"""
        auditor = SovereignRepositoryAuditor(temp_repo)
        assert auditor.repo_root == temp_repo
        assert auditor.results == []
    
    def test_repo_structure_check_pass(self, temp_repo):
        """Test repository structure check - passing"""
        auditor = SovereignRepositoryAuditor(temp_repo)
        auditor._check_repo_structure()
        
        result = auditor.results[0]
        assert result.category == "repo_structure"
        assert result.status == "PASS"
    
    def test_repo_structure_check_missing(self, temp_repo):
        """Test repository structure check - missing directories"""
        # Remove a required directory
        shutil.rmtree(temp_repo / "docs")
        
        auditor = SovereignRepositoryAuditor(temp_repo)
        auditor._check_repo_structure()
        
        result = auditor.results[0]
        assert result.category == "repo_structure"
        assert result.status == "WARNING"
    
    def test_dependencies_check(self, temp_repo):
        """Test dependencies check"""
        auditor = SovereignRepositoryAuditor(temp_repo)
        auditor._check_dependencies()
        
        # Should check Python and Node.js dependencies
        categories = [r.category for r in auditor.results]
        assert categories.count("dependencies") >= 2
    
    def test_config_files_check(self, temp_repo):
        """Test config files check"""
        auditor = SovereignRepositoryAuditor(temp_repo)
        auditor._check_config_files()
        
        # Should check README.md, .gitignore, .env.example
        check_names = [r.check_name for r in auditor.results]
        assert "README.md" in check_names
        assert ".gitignore" in check_names
    
    def test_documentation_check(self, temp_repo):
        """Test documentation check"""
        auditor = SovereignRepositoryAuditor(temp_repo)
        auditor._check_documentation()
        
        result = auditor.results[0]
        assert result.category == "documentation"
        assert result.status == "PASS"
        assert result.details["count"] >= 1
    
    def test_security_files_check(self, temp_repo):
        """Test security files check"""
        auditor = SovereignRepositoryAuditor(temp_repo)
        auditor._check_security_files()
        
        result = auditor.results[0]
        assert result.category == "security"
        assert result.status == "PASS"
    
    def test_workflows_check(self, temp_repo):
        """Test workflows check"""
        auditor = SovereignRepositoryAuditor(temp_repo)
        auditor._check_workflows()
        
        result = auditor.results[0]
        assert result.category == "ci_cd"
        assert result.status == "PASS"
    
    def test_full_audit(self, temp_repo):
        """Test full repository audit"""
        auditor = SovereignRepositoryAuditor(temp_repo)
        results = auditor.audit(auto_repair=False)
        
        # Should have multiple results
        assert len(results) > 0
        
        # Check categories
        categories = set(r.category for r in results)
        assert "repo_structure" in categories
        assert "dependencies" in categories
        assert "config_files" in categories


class TestSovereignAuditOrchestrator:
    """Test audit orchestrator"""
    
    @pytest.fixture
    def temp_repo(self):
        """Create a temporary repository with all necessary files"""
        temp_dir = tempfile.mkdtemp()
        repo_path = Path(temp_dir)
        
        # Initialize git
        subprocess.run(['git', 'init'], cwd=repo_path, check=True, capture_output=True)
        subprocess.run(['git', 'config', 'user.name', 'Test User'], cwd=repo_path, check=True, capture_output=True)
        subprocess.run(['git', 'config', 'user.email', 'test@example.com'], cwd=repo_path, check=True, capture_output=True)
        subprocess.run(['git', 'checkout', '-b', 'test-branch'], cwd=repo_path, check=True, capture_output=True)
        
        # Create basic structure
        (repo_path / "bridge_backend").mkdir()
        (repo_path / "bridge-frontend").mkdir()
        (repo_path / "scripts").mkdir()
        (repo_path / "docs").mkdir()
        
        # Create files
        (repo_path / "README.md").write_text("# Test\n")
        (repo_path / ".gitignore").write_text("*.env\n__pycache__\nnode_modules\n.DS_Store\n")
        (repo_path / "netlify.toml").write_text("[build]\n[[headers]]\n")
        
        yield repo_path
        
        # Cleanup
        shutil.rmtree(temp_dir)
    
    @patch('subprocess.run')
    def test_orchestrator_initialization(self, mock_run, temp_repo):
        """Test orchestrator initialization"""
        # Mock git commands
        mock_run.return_value = Mock(returncode=0, stdout="test-branch\n")
        
        orchestrator = SovereignAuditOrchestrator(str(temp_repo))
        assert orchestrator.repo_root == temp_repo
    
    @patch('subprocess.run')
    def test_get_repo_info(self, mock_run, temp_repo):
        """Test getting repository info"""
        # Mock git commands
        def side_effect(*args, **kwargs):
            cmd = args[0]
            if "remote.origin.url" in cmd:
                return Mock(returncode=0, stdout="https://github.com/test/repo.git\n")
            elif "branch" in cmd:
                return Mock(returncode=0, stdout="main\n")
            elif "rev-parse" in cmd:
                return Mock(returncode=0, stdout="abc123def456\n")
            return Mock(returncode=1, stdout="")
        
        mock_run.side_effect = side_effect
        
        orchestrator = SovereignAuditOrchestrator(str(temp_repo))
        info = orchestrator._get_repo_info()
        
        assert "repository" in info
        assert "branch" in info
        assert "commit" in info
    
    def test_generate_summary(self, temp_repo):
        """Test summary generation"""
        results = [
            AuditResult("test", "check1", "PASS", "Test 1", severity="INFO"),
            AuditResult("test", "check2", "PASS", "Test 2", severity="INFO"),
            AuditResult("test", "check3", "WARNING", "Test 3", severity="LOW"),
            AuditResult("test", "check4", "FAIL", "Test 4", severity="HIGH"),
        ]
        repairs = []
        
        orchestrator = SovereignAuditOrchestrator(str(temp_repo))
        summary = orchestrator._generate_summary(results, repairs)
        
        assert summary["total_checks"] == 4
        assert summary["passed"] == 2
        assert summary["warnings"] == 1
        assert summary["failed"] == 1
        assert summary["status"] == "NEEDS_ATTENTION"
        assert 0 <= summary["score"] <= 100


class TestIntegration:
    """Integration tests"""
    
    def test_audit_result_to_dict(self):
        """Test converting audit result to dictionary"""
        from dataclasses import asdict
        
        result = AuditResult(
            category="test",
            check_name="test_check",
            status="PASS",
            message="Test passed",
            details={"key": "value"},
            severity="INFO",
            auto_repair_available=True,
            repaired=False
        )
        
        result_dict = asdict(result)
        assert result_dict["category"] == "test"
        assert result_dict["check_name"] == "test_check"
        assert result_dict["details"] == {"key": "value"}
    
    def test_json_serialization(self):
        """Test JSON serialization of audit results"""
        from dataclasses import asdict
        
        result = AuditResult(
            category="test",
            check_name="test_check",
            status="PASS",
            message="Test passed"
        )
        
        result_dict = asdict(result)
        json_str = json.dumps(result_dict)
        
        # Should be valid JSON
        loaded = json.loads(json_str)
        assert loaded["category"] == "test"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
