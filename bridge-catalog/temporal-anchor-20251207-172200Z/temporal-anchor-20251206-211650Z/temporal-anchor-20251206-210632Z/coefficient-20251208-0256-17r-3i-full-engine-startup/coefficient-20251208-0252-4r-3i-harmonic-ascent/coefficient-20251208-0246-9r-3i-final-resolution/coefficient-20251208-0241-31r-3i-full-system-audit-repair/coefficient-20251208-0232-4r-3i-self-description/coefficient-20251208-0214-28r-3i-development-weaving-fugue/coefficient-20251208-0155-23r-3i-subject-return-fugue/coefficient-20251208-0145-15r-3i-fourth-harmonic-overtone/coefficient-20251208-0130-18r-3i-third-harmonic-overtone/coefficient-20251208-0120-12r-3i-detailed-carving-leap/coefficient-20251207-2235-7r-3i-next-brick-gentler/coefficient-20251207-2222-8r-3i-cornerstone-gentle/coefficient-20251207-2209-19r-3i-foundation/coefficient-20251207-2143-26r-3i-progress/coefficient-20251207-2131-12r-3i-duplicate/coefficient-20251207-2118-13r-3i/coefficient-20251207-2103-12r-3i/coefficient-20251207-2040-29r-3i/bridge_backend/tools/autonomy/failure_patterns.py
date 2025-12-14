"""
Failure Pattern Definitions for Autonomous Workflow Healing

This module defines common failure patterns and their solutions.
"""

FAILURE_PATTERNS = {
    "browser_download_blocked": {
        "detection": "googlechromelabs.github.io|storage.googleapis.com",
        "solution": "use_playwright_system_browsers",
        "priority": "CRITICAL",
        "description": "Browser download blocked by firewall",
        "auto_fixable": True,
        "fix_steps": [
            "Add Playwright installation step",
            "Configure environment variables to skip Puppeteer download",
            "Use system-installed browsers"
        ]
    },
    "forge_auth_failure": {
        "detection": "FORGE_DOMINION_ROOT.*missing|DOMINION_SEAL",
        "solution": "inject_ephemeral_tokens",
        "priority": "HIGH",
        "description": "Forge authentication credentials missing",
        "auto_fixable": False,
        "fix_steps": [
            "Configure FORGE_DOMINION_ROOT secret",
            "Configure DOMINION_SEAL secret",
            "Verify Forge integration settings"
        ]
    },
    "container_health_timeout": {
        "detection": "health check.*failed|timeout",
        "solution": "adjust_health_check_intervals",
        "priority": "MEDIUM",
        "description": "Container health check timeout",
        "auto_fixable": True,
        "fix_steps": [
            "Increase timeout duration",
            "Add retry logic",
            "Optimize health check endpoint"
        ]
    },
    "deprecated_actions": {
        "detection": "actions/upload-artifact@v3|actions/download-artifact@v3",
        "solution": "update_action_versions",
        "priority": "LOW",
        "description": "Using deprecated GitHub Actions",
        "auto_fixable": True,
        "fix_steps": [
            "Update actions/upload-artifact to v4",
            "Update actions/download-artifact to v4",
            "Update actions/setup-node to v4"
        ]
    },
    "missing_dependencies": {
        "detection": "ModuleNotFoundError|ImportError|Cannot find module",
        "solution": "install_dependencies",
        "priority": "HIGH",
        "description": "Missing Python or Node.js dependencies",
        "auto_fixable": True,
        "fix_steps": [
            "Run pip install -r requirements.txt",
            "Run npm ci",
            "Verify dependency versions"
        ]
    },
    "timeout_issues": {
        "detection": "ETIMEDOUT|timeout.*exceeded|operation.*timed out",
        "solution": "increase_timeouts",
        "priority": "MEDIUM",
        "description": "Operation timeout",
        "auto_fixable": True,
        "fix_steps": [
            "Add timeout-minutes to step",
            "Increase network timeout values",
            "Add retry logic for transient failures"
        ]
    },
    "environment_mismatch": {
        "detection": "ENOENT|file not found|directory.*does not exist",
        "solution": "verify_paths",
        "priority": "MEDIUM",
        "description": "File or directory not found",
        "auto_fixable": True,
        "fix_steps": [
            "Verify file paths are correct",
            "Check working directory",
            "Ensure checkout step is included"
        ]
    }
}


def get_pattern(pattern_name: str) -> dict:
    """Get a specific failure pattern by name."""
    return FAILURE_PATTERNS.get(pattern_name, {})


def get_all_patterns() -> dict:
    """Get all failure patterns."""
    return FAILURE_PATTERNS


def is_auto_fixable(pattern_name: str) -> bool:
    """Check if a pattern is auto-fixable."""
    pattern = get_pattern(pattern_name)
    return pattern.get("auto_fixable", False)


def get_priority(pattern_name: str) -> str:
    """Get the priority of a pattern."""
    pattern = get_pattern(pattern_name)
    return pattern.get("priority", "UNKNOWN")
