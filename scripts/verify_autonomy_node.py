#!/usr/bin/env python3
"""
Embedded Autonomy Node Verification Script
v1.9.7n

This script verifies that the EAN implementation is complete and functional.
"""
import os
import sys
import json
import importlib.util
from pathlib import Path


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'


def check_exists(path, description):
    """Check if a file or directory exists"""
    if os.path.exists(path):
        print(f"{Colors.GREEN}✅{Colors.RESET} {description}: {path}")
        return True
    else:
        print(f"{Colors.RED}❌{Colors.RESET} {description} NOT FOUND: {path}")
        return False


def check_json_valid(path, description):
    """Check if a JSON file is valid"""
    if not check_exists(path, description):
        return False
    
    try:
        with open(path, 'r') as f:
            json.load(f)
        print(f"{Colors.GREEN}✅{Colors.RESET} {description} is valid JSON")
        return True
    except json.JSONDecodeError as e:
        print(f"{Colors.RED}❌{Colors.RESET} {description} is INVALID JSON: {e}")
        return False


def check_python_module(path, description):
    """Check if a Python module can be imported"""
    if not check_exists(path, description):
        return False
    
    try:
        spec = importlib.util.spec_from_file_location("test_module", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        print(f"{Colors.GREEN}✅{Colors.RESET} {description} imports successfully")
        return True
    except Exception as e:
        print(f"{Colors.RED}❌{Colors.RESET} {description} import FAILED: {e}")
        return False


def main():
    """Run all verification checks"""
    print(f"\n{Colors.BLUE}🚀 Embedded Autonomy Node Verification{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}\n")
    
    repo_root = Path(__file__).parent.parent
    os.chdir(repo_root)
    
    all_passed = True
    
    # 1. Check directory structure
    print(f"\n{Colors.BLUE}📁 Checking Directory Structure{Colors.RESET}")
    print("-" * 60)
    
    checks = [
        (f"{repo_root}/.github/autonomy_node", "Autonomy Node directory"),
        (f"{repo_root}/.github/autonomy_node/reports", "Reports directory"),
        (f"{repo_root}/.github/workflows", "Workflows directory"),
    ]
    
    for path, desc in checks:
        all_passed &= check_exists(path, desc)
    
    # 2. Check core Python files
    print(f"\n{Colors.BLUE}🐍 Checking Core Python Files{Colors.RESET}")
    print("-" * 60)
    
    python_files = [
        (f"{repo_root}/.github/autonomy_node/__init__.py", "__init__.py"),
        (f"{repo_root}/.github/autonomy_node/core.py", "core.py"),
        (f"{repo_root}/.github/autonomy_node/truth.py", "truth.py"),
        (f"{repo_root}/.github/autonomy_node/parser.py", "parser.py"),
        (f"{repo_root}/.github/autonomy_node/cascade.py", "cascade.py"),
        (f"{repo_root}/.github/autonomy_node/blueprint.py", "blueprint.py"),
    ]
    
    for path, desc in python_files:
        all_passed &= check_python_module(path, desc)
    
    # 3. Check configuration files
    print(f"\n{Colors.BLUE}⚙️ Checking Configuration Files{Colors.RESET}")
    print("-" * 60)
    
    all_passed &= check_json_valid(
        f"{repo_root}/.github/autonomy_node/node_config.json",
        "node_config.json"
    )
    
    # 4. Check workflow file
    print(f"\n{Colors.BLUE}🔄 Checking Workflow Files{Colors.RESET}")
    print("-" * 60)
    
    all_passed &= check_exists(
        f"{repo_root}/.github/workflows/autonomy_node.yml",
        "autonomy_node.yml workflow"
    )
    
    # 5. Check Genesis integration
    print(f"\n{Colors.BLUE}🌌 Checking Genesis Integration{Colors.RESET}")
    print("-" * 60)
    
    all_passed &= check_python_module(
        f"{repo_root}/bridge_backend/genesis/registration.py",
        "registration.py"
    )
    
    # Verify Genesis __init__.py includes registration
    genesis_init = f"{repo_root}/bridge_backend/genesis/__init__.py"
    if check_exists(genesis_init, "Genesis __init__.py"):
        with open(genesis_init, 'r') as f:
            content = f.read()
            if "register_embedded_nodes" in content:
                print(f"{Colors.GREEN}✅{Colors.RESET} Genesis __init__.py exports register_embedded_nodes")
            else:
                print(f"{Colors.RED}❌{Colors.RESET} Genesis __init__.py missing register_embedded_nodes export")
                all_passed = False
    else:
        all_passed = False
    
    # Verify Genesis bus includes topics
    genesis_bus = f"{repo_root}/bridge_backend/genesis/bus.py"
    if check_exists(genesis_bus, "Genesis bus.py"):
        with open(genesis_bus, 'r') as f:
            content = f.read()
            required_topics = [
                "genesis.node.register",
                "genesis.autonomy_node.report",
                "autonomy_node.scan.complete",
                "autonomy_node.repair.applied",
            ]
            
            for topic in required_topics:
                if topic in content:
                    print(f"{Colors.GREEN}✅{Colors.RESET} Genesis bus includes topic: {topic}")
                else:
                    print(f"{Colors.RED}❌{Colors.RESET} Genesis bus missing topic: {topic}")
                    all_passed = False
    else:
        all_passed = False
    
    # 6. Check documentation
    print(f"\n{Colors.BLUE}📚 Checking Documentation{Colors.RESET}")
    print("-" * 60)
    
    docs = [
        (f"{repo_root}/docs/EMBEDDED_AUTONOMY_NODE.md", "EMBEDDED_AUTONOMY_NODE.md"),
        (f"{repo_root}/docs/GITHUB_MINI_BRIDGE_OVERVIEW.md", "GITHUB_MINI_BRIDGE_OVERVIEW.md"),
        (f"{repo_root}/docs/NODE_FAILSAFE_GUIDE.md", "NODE_FAILSAFE_GUIDE.md"),
        (f"{repo_root}/docs/GENESIS_REGISTRATION_OVERVIEW.md", "GENESIS_REGISTRATION_OVERVIEW.md"),
    ]
    
    for path, desc in docs:
        all_passed &= check_exists(path, desc)
    
    # 7. Check .gitignore
    print(f"\n{Colors.BLUE}📝 Checking .gitignore{Colors.RESET}")
    print("-" * 60)
    
    gitignore = f"{repo_root}/.gitignore"
    if check_exists(gitignore, ".gitignore"):
        with open(gitignore, 'r') as f:
            content = f.read()
            if ".github/autonomy_node/reports/" in content:
                print(f"{Colors.GREEN}✅{Colors.RESET} .gitignore includes reports directory")
            else:
                print(f"{Colors.YELLOW}⚠️{Colors.RESET} .gitignore may not include reports directory (optional)")
    
    # 8. Test functionality
    print(f"\n{Colors.BLUE}🧪 Testing Functionality{Colors.RESET}")
    print("-" * 60)
    
    try:
        # Import and test core modules
        sys.path.insert(0, f"{repo_root}/.github/autonomy_node")
        
        import truth
        import parser
        import cascade
        import blueprint
        
        # Test basic functionality
        test_findings = {"test.py": {"status": "warn", "reason": "test"}}
        test_fixes = blueprint.repair(test_findings)
        truth.verify(test_fixes)
        cascade.sync_state()
        
        print(f"{Colors.GREEN}✅{Colors.RESET} All components function correctly")
    except Exception as e:
        print(f"{Colors.RED}❌{Colors.RESET} Functionality test FAILED: {e}")
        all_passed = False
    
    # Summary
    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    if all_passed:
        print(f"{Colors.GREEN}✅ All verification checks PASSED!{Colors.RESET}")
        print(f"\n{Colors.GREEN}🚀 Embedded Autonomy Node is ready for deployment.{Colors.RESET}\n")
        return 0
    else:
        print(f"{Colors.RED}❌ Some verification checks FAILED.{Colors.RESET}")
        print(f"\n{Colors.RED}Please review the errors above and fix them.{Colors.RESET}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
