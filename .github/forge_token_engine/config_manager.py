#!/usr/bin/env python3
"""
Configuration Management for Forge Token Engine

Centralizes all configuration values including:
- Provider limits and costs
- Alert thresholds  
- Baseline cost tracking values
- Workflow estimation parameters
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional


class ForgeConfig:
    """Central configuration management for Forge Token Engine"""
    
    _instance = None
    _config = None
    
    def __new__(cls):
        """Singleton pattern to ensure single config instance"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self):
        """Load configuration from config.json"""
        config_path = Path(__file__).parent / "config.json"
        
        if config_path.exists():
            with open(config_path, 'r') as f:
                self._config = json.load(f)
        else:
            # Default configuration if file doesn't exist
            self._config = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Default configuration values"""
        return {
            "providers": {
                "github_actions": {
                    "enabled": True,
                    "cost_per_minute": 0.008,
                    "free_tier_minutes": 2000
                },
                "render_free": {
                    "enabled": True,
                    "cost_per_minute": 0.0,
                    "free_tier_minutes": 45000
                },
                "netlify_free": {
                    "enabled": True,
                    "cost_per_minute": 0.0,
                    "free_tier_minutes": 300
                },
                "vercel_free": {
                    "enabled": True,
                    "cost_per_minute": 0.0,
                    "free_tier_minutes": 6000
                },
                "self_hosted": {
                    "enabled": True,
                    "cost_per_minute": 0.0,
                    "free_tier_minutes": 999999
                }
            },
            "cost_tracking": {
                "baseline_monthly_cost": 75.0,
                "baseline_monthly_minutes": 3010,
                "baseline_pushes_per_month": 43
            },
            "alerts": {
                "warning_threshold_percent": 70,
                "critical_threshold_percent": 90
            },
            "workflow_estimation": {
                "average_minutes_per_job": 5,
                "pushes_per_month": 43,
                "pull_requests_per_month": 10,
                "schedule_runs_per_month": 30,
                "manual_runs_per_month": 2
            }
        }
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.
        
        Example: config.get('providers.github_actions.cost_per_minute')
        """
        keys = key_path.split('.')
        value = self._config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def get_provider_config(self, provider_name: str) -> Dict[str, Any]:
        """Get configuration for a specific provider"""
        return self.get(f'providers.{provider_name}', {})
    
    def get_cost_per_minute(self, provider_name: str) -> float:
        """Get cost per minute for a provider"""
        return self.get(f'providers.{provider_name}.cost_per_minute', 0.0)
    
    def get_free_tier_minutes(self, provider_name: str) -> int:
        """Get free tier minutes for a provider"""
        return self.get(f'providers.{provider_name}.free_tier_minutes', 0)
    
    def get_baseline_cost(self) -> float:
        """Get baseline monthly cost"""
        return self.get('cost_tracking.baseline_monthly_cost', 75.0)
    
    def get_baseline_minutes(self) -> int:
        """Get baseline monthly minutes"""
        return self.get('cost_tracking.baseline_monthly_minutes', 3010)
    
    def get_baseline_pushes(self) -> int:
        """Get baseline pushes per month"""
        return self.get('cost_tracking.baseline_pushes_per_month', 43)
    
    def get_warning_threshold(self) -> int:
        """Get warning alert threshold percentage"""
        return self.get('alerts.warning_threshold_percent', 70)
    
    def get_critical_threshold(self) -> int:
        """Get critical alert threshold percentage"""
        return self.get('alerts.critical_threshold_percent', 90)
    
    def get_average_job_minutes(self) -> int:
        """Get estimated average minutes per job"""
        return self.get('workflow_estimation.average_minutes_per_job', 5)
    
    def get_monthly_pushes(self) -> int:
        """Get estimated monthly push events"""
        return self.get('workflow_estimation.pushes_per_month', 43)
    
    def get_monthly_prs(self) -> int:
        """Get estimated monthly pull requests"""
        return self.get('workflow_estimation.pull_requests_per_month', 10)
    
    def get_monthly_schedule_runs(self) -> int:
        """Get estimated monthly scheduled runs"""
        return self.get('workflow_estimation.schedule_runs_per_month', 30)
    
    def update_baseline(self, cost: float, minutes: int, pushes: int):
        """Update baseline tracking values"""
        if 'cost_tracking' not in self._config:
            self._config['cost_tracking'] = {}
        
        self._config['cost_tracking']['baseline_monthly_cost'] = cost
        self._config['cost_tracking']['baseline_monthly_minutes'] = minutes
        self._config['cost_tracking']['baseline_pushes_per_month'] = pushes
        
        self._save_config()
    
    def _save_config(self):
        """Save configuration back to file"""
        config_path = Path(__file__).parent / "config.json"
        with open(config_path, 'w') as f:
            json.dump(self._config, f, indent=2)
    
    @property
    def all(self) -> Dict[str, Any]:
        """Get entire configuration dictionary"""
        return self._config.copy()


# Global config instance
config = ForgeConfig()


# Convenience functions for common operations
def get_provider_cost(provider: str) -> float:
    """Get cost per minute for a provider"""
    return config.get_cost_per_minute(provider)


def get_provider_quota(provider: str) -> int:
    """Get free tier quota for a provider"""
    return config.get_free_tier_minutes(provider)


def get_github_actions_cost() -> float:
    """Get GitHub Actions cost per minute"""
    return config.get_cost_per_minute('github_actions')


if __name__ == "__main__":
    # Test configuration loading
    print("Forge Token Engine Configuration")
    print("=" * 50)
    print(f"\nGitHub Actions cost/min: ${config.get_cost_per_minute('github_actions')}")
    print(f"Render free tier: {config.get_free_tier_minutes('render_free')} minutes")
    print(f"Baseline monthly cost: ${config.get_baseline_cost()}")
    print(f"Warning threshold: {config.get_warning_threshold()}%")
    print(f"\nAll configuration:")
    print(json.dumps(config.all, indent=2))
