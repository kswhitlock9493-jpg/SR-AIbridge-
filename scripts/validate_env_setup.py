#!/usr/bin/env python3
"""
Comprehensive validation script for SR-AIbridge environment configuration.
Tests all environment files, configuration files, and backend config loading.
"""

import os
import sys
from pathlib import Path

def test_environment_files():
    """Validate all environment template files exist."""
    print("🔍 Testing Environment Files...")
    
    env_files = {
        '.env': 'Local development environment',
        '.env.example': 'Environment variable template',
        '.env.netlify': 'Netlify frontend configuration',
        '.env.production': 'Production source of truth',
        '.env.render.example': 'Render backend template',
        '.env.deploy': 'Deployment configuration'
    }
    
    missing = []
    for filename, description in env_files.items():
        if Path(filename).exists():
            print(f"  ✓ {filename}: {description}")
        else:
            print(f"  ✗ {filename}: {description} (MISSING)")
            missing.append(filename)
    
    if missing:
        print(f"\n❌ Missing {len(missing)} environment file(s)")
        return False
    
    print("✅ All environment files exist\n")
    return True


def test_netlify_config():
    """Validate netlify.toml configuration."""
    print("🔍 Testing Netlify Configuration...")
    
    try:
        import toml
        with open('netlify.toml', 'r') as f:
            config = toml.load(f)
        
        # Verify build configuration
        build = config.get('build', {})
        required_build_keys = ['base', 'command', 'publish']
        for key in required_build_keys:
            if key in build:
                print(f"  ✓ build.{key}: {build[key]}")
            else:
                print(f"  ✗ build.{key}: MISSING")
                return False
        
        # Verify build environment
        build_env = build.get('environment', {})
        required_env_vars = ['NODE_ENV', 'SECRETS_SCAN_ENABLED', 'VITE_API_BASE', 'REACT_APP_API_URL']
        for key in required_env_vars:
            if key in build_env:
                print(f"  ✓ build.environment.{key}: {build_env[key]}")
            else:
                print(f"  ✗ build.environment.{key}: MISSING")
                return False
        
        # Verify redirects exist
        redirects = config.get('redirects', [])
        if redirects:
            print(f"  ✓ Redirects: {len(redirects)} configured")
        else:
            print(f"  ⚠ Redirects: None configured")
        
        print("✅ netlify.toml is valid\n")
        return True
        
    except Exception as e:
        print(f"❌ netlify.toml validation failed: {e}\n")
        return False


def test_render_config():
    """Validate render.yaml configuration."""
    print("🔍 Testing Render Configuration...")
    
    try:
        import yaml
        with open('render.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        services = config.get('services', [])
        if not services:
            print("  ✗ No services defined in render.yaml")
            return False
        
        service = services[0]
        print(f"  ✓ Service: {service.get('name', 'UNNAMED')}")
        print(f"  ✓ Type: {service.get('type', 'UNSPECIFIED')}")
        print(f"  ✓ Environment: {service.get('env', 'UNSPECIFIED')}")
        
        # Verify critical environment variables
        env_vars = service.get('envVars', [])
        critical_vars = [
            'DATABASE_URL',
            'DATABASE_TYPE', 
            'BRIDGE_API_URL',
            'SECRET_KEY',
            'LOG_LEVEL',
            'CASCADE_MODE',
            'VAULT_URL',
            'FEDERATION_SYNC_KEY'
        ]
        
        defined_keys = [var.get('key') for var in env_vars]
        print(f"  ✓ Total environment variables: {len(env_vars)}")
        
        missing = []
        for key in critical_vars:
            if key in defined_keys:
                print(f"    ✓ {key}")
            else:
                print(f"    ✗ {key} (MISSING)")
                missing.append(key)
        
        if missing:
            print(f"\n❌ Missing {len(missing)} critical environment variable(s)")
            return False
        
        print("✅ render.yaml is valid\n")
        return True
        
    except Exception as e:
        print(f"❌ render.yaml validation failed: {e}\n")
        return False


def test_backend_config():
    """Test backend config.py loads correctly with new environment variables."""
    print("🔍 Testing Backend Configuration...")
    
    # Set test environment variables
    test_env = {
        'BRIDGE_API_URL': 'https://test.example.com',
        'SECRET_KEY': 'test-secret-key-32-characters-long',
        'LOG_LEVEL': 'debug',
        'DATABASE_TYPE': 'sqlite',
        'DATABASE_URL': 'sqlite:///test.db',
        'CASCADE_MODE': 'production',
        'VAULT_URL': 'https://vault.example.com',
        'FEDERATION_SYNC_KEY': 'test-federation-key',
        'DATADOG_REGION': 'us'
    }
    
    for key, value in test_env.items():
        os.environ[key] = value
    
    try:
        sys.path.insert(0, 'bridge_backend')
        from config import settings
        
        # Verify all new attributes
        required_attrs = [
            'BRIDGE_API_URL',
            'SECRET_KEY',
            'LOG_LEVEL',
            'DATABASE_TYPE',
            'DATABASE_URL',
            'CASCADE_MODE',
            'VAULT_URL',
            'FEDERATION_SYNC_KEY',
            'DATADOG_REGION'
        ]
        
        for attr in required_attrs:
            if hasattr(settings, attr):
                value = getattr(settings, attr)
                # Mask sensitive values
                if 'KEY' in attr or 'SECRET' in attr:
                    display_value = f"{value[:10]}..." if value else "(empty)"
                else:
                    display_value = value
                print(f"  ✓ {attr}: {display_value}")
            else:
                print(f"  ✗ {attr}: MISSING")
                return False
        
        print("✅ Backend config.py loads correctly\n")
        return True
        
    except Exception as e:
        print(f"❌ Backend config validation failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_documentation():
    """Verify documentation files exist."""
    print("🔍 Testing Documentation...")
    
    doc_files = {
        'docs/ENVIRONMENT_SETUP.md': 'Environment setup guide',
        'docs/DEPLOYMENT_SECURITY_FIX.md': 'Deployment security documentation',
        'docs/NETLIFY_RENDER_ENV_SETUP.md': 'Netlify/Render environment setup',
        'DEPLOYMENT.md': 'Main deployment guide',
        'README.md': 'Project README'
    }
    
    missing = []
    for filename, description in doc_files.items():
        if Path(filename).exists():
            print(f"  ✓ {filename}: {description}")
        else:
            print(f"  ✗ {filename}: {description} (MISSING)")
            missing.append(filename)
    
    if missing:
        print(f"\n⚠️ Missing {len(missing)} documentation file(s)")
        # Documentation is not critical for functionality
    
    print("✅ Documentation check complete\n")
    return True


def main():
    """Run all validation tests."""
    print("=" * 60)
    print("SR-AIbridge Environment Configuration Validation")
    print("=" * 60)
    print()
    
    # Install dependencies if needed
    try:
        import toml
        import yaml
        from dotenv import load_dotenv
    except ImportError:
        print("⚠️ Installing required dependencies...")
        os.system("pip3 install toml pyyaml python-dotenv -q")
        print()
    
    results = []
    
    # Run all tests
    results.append(("Environment Files", test_environment_files()))
    results.append(("Netlify Configuration", test_netlify_config()))
    results.append(("Render Configuration", test_render_config()))
    results.append(("Backend Configuration", test_backend_config()))
    results.append(("Documentation", test_documentation()))
    
    # Summary
    print("=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")
        if not passed:
            all_passed = False
    
    print()
    if all_passed:
        print("🎉 All validation tests passed!")
        return 0
    else:
        print("⚠️ Some validation tests failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
