"""Tests for Bridge Code Super-Engine (BCSE)"""
import os
import sys
from unittest.mock import patch, MagicMock
import pytest

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bridge_tools.bcse.config import Policy, DEFAULT_POLICY
from bridge_tools.bcse.forge import dominion_root, fetch_policies
from bridge_tools.bcse.reporters import write_sarif, pr_summary


class TestBCSEConfig:
    """Test BCSE configuration"""
    
    def test_default_policy_exists(self):
        """Test that default policy is defined"""
        assert DEFAULT_POLICY is not None
        assert isinstance(DEFAULT_POLICY, Policy)
        
    def test_default_policy_values(self):
        """Test default policy values"""
        assert DEFAULT_POLICY.coverage_min == 0.80
        assert DEFAULT_POLICY.mypy_strict is True
        assert DEFAULT_POLICY.ruff_severity == "E,W,F"
        assert DEFAULT_POLICY.bandit_min_severity == "MEDIUM"
        assert DEFAULT_POLICY.max_cyclomatic == 10
        assert DEFAULT_POLICY.fail_on_vuln is True
        assert "MIT" in DEFAULT_POLICY.allowed_licenses


class TestForgeIntegration:
    """Test Forge Dominion integration"""
    
    def test_dominion_root_default(self):
        """Test dominion root with no environment variable"""
        with patch.dict(os.environ, {}, clear=True):
            root = dominion_root()
            assert root == "dominion://local"
    
    def test_dominion_root_from_env(self):
        """Test dominion root from environment variable"""
        with patch.dict(os.environ, {"FORGE_DOMINION_ROOT": "https://forge.example.com"}):
            root = dominion_root()
            assert root == "https://forge.example.com"
    
    def test_fetch_policies_no_url(self):
        """Test fetch_policies with no URL configured"""
        with patch.dict(os.environ, {}, clear=True):
            policies = fetch_policies()
            assert isinstance(policies, dict)
    
    @patch('urllib.request.urlopen')
    def test_fetch_policies_from_url(self, mock_urlopen):
        """Test fetch_policies from Forge URL"""
        # Mock response
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"coverage_min": 0.85}'
        mock_response.__enter__ = lambda self: self
        mock_response.__exit__ = lambda self, *args: None
        mock_urlopen.return_value = mock_response
        
        with patch.dict(os.environ, {
            "FORGE_POLICY_URL": "https://forge.example.com/policy",
            "DOMINION_SEAL": "test_token"
        }):
            policies = fetch_policies()
            assert isinstance(policies, dict)
            assert policies.get("coverage_min") == 0.85


class TestReporters:
    """Test BCSE reporters"""
    
    def test_write_sarif(self, tmp_path):
        """Test SARIF report writing"""
        sarif_obj = {
            "version": "2.1.0",
            "runs": []
        }
        output_file = tmp_path / "test.sarif"
        write_sarif(sarif_obj, str(output_file))
        
        assert output_file.exists()
        
        import json
        with open(output_file) as f:
            data = json.load(f)
            assert data["version"] == "2.1.0"
    
    def test_pr_summary(self, tmp_path):
        """Test PR summary generation"""
        items = [
            {"name": "black", "status": "OK"},
            {"name": "ruff", "status": "FAIL"}
        ]
        output_file = tmp_path / "summary.md"
        pr_summary(items, str(output_file))
        
        assert output_file.exists()
        content = output_file.read_text()
        assert "black" in content
        assert "ruff" in content


class TestCLI:
    """Test BCSE CLI"""
    
    def test_cli_help(self):
        """Test CLI help output"""
        from bridge_tools.bcse import cli
        import subprocess
        
        result = subprocess.run(
            [sys.executable, "-m", "bridge_tools.bcse.cli", "--help"],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert "analyze" in result.stdout
        assert "fix" in result.stdout


class TestSovereignMode:
    """Test Sovereign Git integration - always enabled"""
    
    def test_sovereign_git_always_enabled(self):
        """Test that Sovereign Git mode is always enabled"""
        # BCSE should always respect Forge Dominion settings
        # This is the "always enabled" requirement from placeholder mode
        from bridge_tools.bcse.config import BCSE_ALWAYS_ENABLED
        
        assert BCSE_ALWAYS_ENABLED is True, "BCSE must always be enabled"
        
        with patch.dict(os.environ, {"FORGE_DOMINION_ROOT": "dominion://local"}):
            root = dominion_root()
            assert root is not None
            # Sovereign mode is always on - it checks for Forge settings
            assert "dominion" in root.lower() or root.startswith("http")
    
    def test_placeholder_mode_reveals_gates(self):
        """Test that placeholder mode reveals all gates"""
        # In placeholder mode, all gates should be visible and configurable
        from bridge_tools.bcse.config import PLACEHOLDER_MODE
        from bridge_tools.bcse.cli import load_policy
        
        assert PLACEHOLDER_MODE is True, "Placeholder mode must be active"
        
        # This should work whether or not Forge is configured
        policy = load_policy()
        assert policy is not None
        
        # All gates are revealed (accessible)
        assert hasattr(policy, 'coverage_min')
        assert hasattr(policy, 'mypy_strict')
        assert hasattr(policy, 'ruff_severity')
        assert hasattr(policy, 'bandit_min_severity')
        assert hasattr(policy, 'max_cyclomatic')
        assert hasattr(policy, 'fail_on_vuln')
        assert hasattr(policy, 'allowed_licenses')
    
    def test_gates_command_exists(self):
        """Test that gates command is available"""
        from bridge_tools.bcse import cli
        import subprocess
        
        result = subprocess.run(
            [sys.executable, "-m", "bridge_tools.bcse.cli", "--help"],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert "gates" in result.stdout, "gates command must be available"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
