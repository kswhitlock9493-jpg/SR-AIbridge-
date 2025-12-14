#!/usr/bin/env python3
"""
Tests for Firewall Sovereignty Framework
"""

import os
import sys
import pytest
import json
import yaml
from pathlib import Path

# Add bridge_backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from bridge_backend.tools.firewall_sovereignty.firewall_config_manager import FirewallConfigManager
from bridge_backend.tools.firewall_sovereignty.network_resilience import NetworkResilienceLayer
from bridge_backend.tools.firewall_sovereignty.validation_sovereignty import ValidationSovereignty
from bridge_backend.tools.firewall_sovereignty.script_execution import ScriptExecutionSovereignty


class TestFirewallConfigManager:
    """Tests for Firewall Configuration Manager"""
    
    def test_initialization(self, tmp_path):
        """Test that manager initializes correctly"""
        manager = FirewallConfigManager(config_dir=str(tmp_path))
        assert manager.config_dir == tmp_path
        assert manager.allowlist is not None
        assert manager.egress_policies is not None
        assert manager.firewall_rules is not None
    
    def test_add_domain_to_allowlist(self, tmp_path):
        """Test adding domain to allowlist"""
        manager = FirewallConfigManager(config_dir=str(tmp_path))
        
        result = manager.add_domain_to_allowlist("example.com", "critical")
        assert result is True
        assert manager.is_domain_allowed("example.com")
        
        # Adding again should return False (already exists)
        result = manager.add_domain_to_allowlist("example.com", "critical")
        assert result is False
    
    def test_remove_domain_from_allowlist(self, tmp_path):
        """Test removing domain from allowlist"""
        manager = FirewallConfigManager(config_dir=str(tmp_path))
        
        manager.add_domain_to_allowlist("test.com", "critical")
        assert manager.is_domain_allowed("test.com")
        
        result = manager.remove_domain_from_allowlist("test.com")
        assert result is True
        assert not manager.is_domain_allowed("test.com")
    
    def test_validate_firewall_config(self, tmp_path):
        """Test firewall configuration validation"""
        manager = FirewallConfigManager(config_dir=str(tmp_path))
        
        validation = manager.validate_firewall_config()
        assert validation["valid"] is True
        assert isinstance(validation["errors"], list)
        assert isinstance(validation["warnings"], list)
    
    def test_export_config(self, tmp_path):
        """Test configuration export"""
        manager = FirewallConfigManager(config_dir=str(tmp_path))
        
        export_file = tmp_path / "export.json"
        manager.export_config(str(export_file))
        
        assert export_file.exists()
        
        with open(export_file, 'r') as f:
            config = json.load(f)
        
        assert "version" in config
        assert "allowlist" in config
        assert "egress_policies" in config
        assert "firewall_rules" in config
    
    def test_get_all_allowed_domains(self, tmp_path):
        """Test getting all allowed domains"""
        manager = FirewallConfigManager(config_dir=str(tmp_path))
        
        domains = manager.get_all_allowed_domains()
        assert isinstance(domains, list)
        assert len(domains) > 0  # Should have default domains


class TestNetworkResilienceLayer:
    """Tests for Network Resilience Layer"""
    
    def test_initialization(self):
        """Test that resilience layer initializes correctly"""
        resilience = NetworkResilienceLayer()
        assert resilience.config is not None
        assert resilience.max_retries > 0
        assert resilience.connection_timeout > 0
    
    def test_connection_stats(self):
        """Test connection statistics tracking"""
        resilience = NetworkResilienceLayer()
        
        stats = resilience.get_connection_stats()
        assert "successful_connections" in stats
        assert "failed_connections" in stats
        assert "success_rate_percent" in stats
    
    def test_reset_stats(self):
        """Test resetting connection statistics"""
        resilience = NetworkResilienceLayer()
        
        # Make a connection to populate stats
        resilience.test_connection("https://api.github.com")
        
        stats_before = resilience.get_connection_stats()
        assert stats_before["total_attempts"] > 0
        
        # Reset
        resilience.reset_stats()
        
        stats_after = resilience.get_connection_stats()
        assert stats_after["total_attempts"] == 0
    
    def test_test_connection_success(self):
        """Test successful connection"""
        resilience = NetworkResilienceLayer()
        
        result = resilience.test_connection("https://api.github.com")
        assert "success" in result
        assert "url" in result
    
    def test_batch_health_check(self):
        """Test batch health checking"""
        resilience = NetworkResilienceLayer()
        
        urls = [
            "https://api.github.com",
            "https://pypi.org"
        ]
        
        results = resilience.batch_health_check(urls)
        assert results["total_checked"] == len(urls)
        assert "successful" in results
        assert "failed" in results
        assert "details" in results


class TestValidationSovereignty:
    """Tests for Validation Sovereignty"""
    
    def test_initialization(self):
        """Test that validator initializes correctly"""
        validator = ValidationSovereignty()
        assert validator.validation_rules is not None
        assert "headers" in validator.validation_rules
        assert "netlify_config" in validator.validation_rules
    
    def test_validate_headers(self):
        """Test header validation"""
        validator = ValidationSovereignty()
        
        # Valid headers
        headers = {
            "X-Frame-Options": "SAMEORIGIN",
            "X-Content-Type-Options": "nosniff",
            "Referrer-Policy": "no-referrer"
        }
        
        result = validator.validate_headers(headers)
        assert result["valid"] is True
        assert len(result["errors"]) == 0
    
    def test_validate_headers_missing_required(self):
        """Test header validation with missing required header"""
        validator = ValidationSovereignty()
        
        # Missing required header
        headers = {
            "X-Frame-Options": "SAMEORIGIN"
        }
        
        result = validator.validate_headers(headers)
        assert result["valid"] is False
        assert len(result["errors"]) > 0
    
    def test_validate_netlify_config_file_not_found(self):
        """Test netlify config validation with missing file"""
        validator = ValidationSovereignty()
        
        result = validator.validate_netlify_config("/nonexistent/netlify.toml")
        assert result["valid"] is False
        assert len(result["errors"]) > 0
    
    def test_validate_network_policies(self, tmp_path):
        """Test network policy validation"""
        validator = ValidationSovereignty()
        
        # Create a valid policy file
        policy_file = tmp_path / "test_policy.yaml"
        policy = {
            "version": "1.0.0",
            "domains": {
                "critical": ["example.com", "test.com"]
            }
        }
        
        with open(policy_file, 'w') as f:
            yaml.dump(policy, f)
        
        result = validator.validate_network_policies(str(policy_file))
        assert result["valid"] is True


class TestScriptExecutionSovereignty:
    """Tests for Script Execution Sovereignty"""
    
    def test_initialization(self, tmp_path):
        """Test that executor initializes correctly"""
        executor = ScriptExecutionSovereignty(str(tmp_path))
        assert executor.workspace_root == tmp_path
        assert executor.environment_config is not None
    
    def test_detect_environment(self):
        """Test environment detection"""
        executor = ScriptExecutionSovereignty()
        
        assert "python_version" in executor.environment_config
        assert "python_path" in executor.environment_config
        assert "platform" in executor.environment_config
    
    def test_validate_dependencies_python(self):
        """Test Python dependency validation"""
        executor = ScriptExecutionSovereignty()
        
        result = executor.validate_dependencies("python")
        assert "valid" in result
        assert "missing" in result
        assert "installed" in result
    
    def test_health_check_scripts(self, tmp_path):
        """Test script health checking"""
        executor = ScriptExecutionSovereignty(str(tmp_path))
        
        # Create test scripts
        script1 = tmp_path / "test1.py"
        script1.write_text("#!/usr/bin/env python3\nprint('test')")
        script1.chmod(0o755)
        
        script2 = tmp_path / "test2.sh"
        script2.write_text("#!/bin/bash\necho 'test'")
        
        results = executor.health_check_scripts([str(script1), str(script2)])
        
        assert results["total_scripts"] == 2
        assert results["accessible"] >= 0
        assert "details" in results
    
    def test_execute_script_not_found(self, tmp_path):
        """Test executing non-existent script"""
        executor = ScriptExecutionSovereignty(str(tmp_path))
        
        result = executor.execute_script("/nonexistent/script.py")
        assert result["success"] is False
        assert "error" in result


def test_integration_sovereignty_systems(tmp_path):
    """Integration test for all sovereignty systems"""
    # Initialize all systems
    firewall_manager = FirewallConfigManager(config_dir=str(tmp_path / "network_policies"))
    network_resilience = NetworkResilienceLayer()
    validator = ValidationSovereignty()
    script_executor = ScriptExecutionSovereignty(str(tmp_path))
    
    # Test firewall
    firewall_validation = firewall_manager.validate_firewall_config()
    assert firewall_validation["valid"] is True
    
    # Test network
    health_check = network_resilience.batch_health_check(["https://api.github.com"])
    assert health_check["total_checked"] == 1
    
    # Test validation
    headers = {
        "X-Frame-Options": "SAMEORIGIN",
        "X-Content-Type-Options": "nosniff",
        "Referrer-Policy": "no-referrer"
    }
    header_validation = validator.validate_headers(headers)
    assert header_validation["valid"] is True
    
    # Test script executor
    env_config = script_executor.environment_config
    assert env_config["python_version"] is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
