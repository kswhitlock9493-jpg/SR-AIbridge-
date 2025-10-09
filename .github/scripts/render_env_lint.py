#!/usr/bin/env python3
"""
Render environment linter
Validates render.yaml configuration and environment variables
"""
import sys
import pathlib
import re

def lint_render_config():
    """Lint render.yaml configuration"""
    root = pathlib.Path(__file__).resolve().parents[2]
    render_yaml = root / "render.yaml"
    
    if not render_yaml.exists():
        print("✗ render.yaml not found")
        return 1
    
    content = render_yaml.read_text()
    issues = []
    
    # Check for required fields
    required_checks = [
        ("type: web", "Service type not set to 'web'"),
        ("env: python", "Environment not set to 'python'"),
        ("startCommand:", "Start command not defined"),
        ("healthCheckPath:", "Health check path not defined"),
    ]
    
    for pattern, message in required_checks:
        if pattern not in content:
            issues.append(message)
    
    # Check for required environment variables
    required_vars = [
        "PORT",
        "ENVIRONMENT",
        "DATABASE_URL",
        "BRIDGE_API_URL",
        "SECRET_KEY",
        "LOG_LEVEL",
    ]
    
    for var in required_vars:
        if f"key: {var}" not in content:
            issues.append(f"Missing required env var: {var}")
    
    # Check start command references the correct module (handle multiline)
    if "startCommand:" in content:
        # Handle both inline and multiline startCommand
        if "start.sh" in content or ("startCommand:" in content and "uvicorn" in content):
            # Good - using start.sh or uvicorn
            pass
        else:
            issues.append("Start command should use start.sh or uvicorn")
        
        # Check for PORT reference (could be $PORT or ${PORT})
        if "$PORT" in content or "${PORT}" in content:
            # Good - references PORT
            pass
        else:
            # Only warn if not using start.sh (which sets PORT internally)
            if "start.sh" not in content:
                issues.append("Start command should reference $PORT")
    
    # Check Python version is pinned
    if "PYTHON_VERSION" not in content:
        issues.append("Python version not pinned (should set PYTHON_VERSION)")
    
    # Report results
    if issues:
        print("Render configuration issues found:\n")
        for issue in issues:
            print(f"  ✗ {issue}")
        print(f"\n{len(issues)} issue(s) found")
        return 1
    else:
        print("✓ render.yaml configuration is valid")
        return 0

if __name__ == "__main__":
    sys.exit(lint_render_config())
