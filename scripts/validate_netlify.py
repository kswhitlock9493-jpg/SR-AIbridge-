#!/usr/bin/env python3
"""
Netlify Configuration Validator
Local syntax & semantic validator for netlify.toml
Part of Umbra + Netlify Integration v1.9.7e
"""

import sys
import os
from pathlib import Path
import re

def validate_netlify_toml():
    """Validate netlify.toml syntax and structure"""
    netlify_file = Path("netlify.toml")
    
    if not netlify_file.exists():
        print("❌ netlify.toml not found")
        return False
    
    try:
        content = netlify_file.read_text()
        
        # Check for basic required sections
        required_sections = ["[build]", "[[headers]]", "[[redirects]]"]
        missing = [s for s in required_sections if s not in content]
        
        if missing:
            print(f"❌ Missing required sections: {', '.join(missing)}")
            return False
        
        # Check for duplicate header rules (common issue)
        header_blocks = re.findall(r'\[\[headers\]\].*?(?=\[\[|$)', content, re.DOTALL)
        header_paths = [re.search(r'for\s*=\s*"([^"]+)"', block) for block in header_blocks]
        header_paths = [m.group(1) for m in header_paths if m]
        
        if len(header_paths) != len(set(header_paths)):
            print("❌ Duplicate header rules detected")
            duplicates = [p for p in header_paths if header_paths.count(p) > 1]
            print(f"   Duplicates: {', '.join(set(duplicates))}")
            return False
        
        # Check for duplicate redirect rules
        redirect_blocks = re.findall(r'\[\[redirects\]\].*?(?=\[\[|$)', content, re.DOTALL)
        redirect_paths = []
        for block in redirect_blocks:
            from_match = re.search(r'from\s*=\s*"([^"]+)"', block)
            to_match = re.search(r'to\s*=\s*"([^"]+)"', block)
            if from_match and to_match:
                redirect_paths.append((from_match.group(1), to_match.group(1)))
        
        if len(redirect_paths) != len(set(redirect_paths)):
            print("❌ Duplicate redirect rules detected")
            return False
        
        # Check build command exists
        if 'command = "' not in content:
            print("❌ No build command specified")
            return False
        
        print("✅ netlify.toml syntax validation passed")
        return True
        
    except Exception as e:
        print(f"❌ Failed to validate netlify.toml: {e}")
        return False


def validate_headers():
    """Validate _headers file if present"""
    headers_file = Path("_headers")
    
    if not headers_file.exists():
        print("ℹ️  No _headers file found (optional)")
        return True
    
    try:
        content = headers_file.read_text()
        
        # Basic validation - check for duplicate path definitions
        path_blocks = content.split('\n/')
        paths = [block.split('\n')[0].strip() for block in path_blocks if block.strip()]
        
        if len(paths) != len(set(paths)):
            print("❌ Duplicate header paths in _headers")
            return False
        
        print("✅ _headers file validation passed")
        return True
        
    except Exception as e:
        print(f"❌ Failed to validate _headers: {e}")
        return False


def validate_redirects():
    """Validate _redirects file if present"""
    redirects_file = Path("_redirects")
    
    if not redirects_file.exists():
        print("ℹ️  No _redirects file found (optional)")
        return True
    
    try:
        content = redirects_file.read_text()
        lines = [line.strip() for line in content.split('\n') if line.strip() and not line.startswith('#')]
        
        # Check for duplicate redirect rules
        rules = []
        for line in lines:
            parts = line.split()
            if len(parts) >= 2:
                rules.append((parts[0], parts[1]))
        
        if len(rules) != len(set(rules)):
            print("❌ Duplicate redirect rules in _redirects")
            return False
        
        print("✅ _redirects file validation passed")
        return True
        
    except Exception as e:
        print(f"❌ Failed to validate _redirects: {e}")
        return False


def validate_build_script():
    """Validate netlify build script exists"""
    build_script = Path("scripts/netlify_build.sh")
    
    if not build_script.exists():
        print("⚠️  Build script not found: scripts/netlify_build.sh")
        return True  # Not critical
    
    print("✅ Build script found")
    return True


def main():
    """Run all validation checks"""
    print("=" * 60)
    print("🔍 Netlify Configuration Validator v1.9.7e")
    print("=" * 60)
    print()
    
    results = {
        "netlify_toml": validate_netlify_toml(),
        "headers": validate_headers(),
        "redirects": validate_redirects(),
        "build_script": validate_build_script()
    }
    
    print()
    print("=" * 60)
    print("📊 Validation Summary")
    print("=" * 60)
    
    all_passed = True
    for check, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {check}")
        if not passed:
            all_passed = False
    
    print()
    if all_passed:
        print("🎉 All Netlify validation checks passed!")
        return 0
    else:
        print("⚠️  Some validation checks failed. Review the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
