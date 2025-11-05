#!/usr/bin/env python3
"""
🔍 Sovereign Audit & Repair Orchestrator
================================================================================
Comprehensive audit system for Git, Netlify, and Repository sovereignty

This tool performs:
1. Full Git sovereign checks and repairs
2. Full Netlify configuration audit and repairs
3. Complete repository integrity audit and repairs

Authorization: COSMIC_SOVEREIGNTY
Status: SOVEREIGN_OPERATIVE
================================================================================
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timezone
from dataclasses import dataclass, field, asdict
import re

# Add bridge_backend to path
SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(REPO_ROOT))


@dataclass
class AuditResult:
    """Result of an audit check"""
    category: str
    check_name: str
    status: str  # "PASS", "FAIL", "WARNING", "REPAIRED"
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    severity: str = "INFO"  # "CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"
    auto_repair_available: bool = False
    repaired: bool = False


@dataclass
class AuditReport:
    """Complete audit report"""
    timestamp: str
    repository: str
    branch: str
    commit_hash: str
    audits_performed: List[str]
    results: List[AuditResult]
    summary: Dict[str, Any]
    repair_actions: List[Dict[str, Any]]


class SovereignGitAuditor:
    """Audits and repairs Git sovereign configuration"""
    
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.results: List[AuditResult] = []
    
    def audit(self, auto_repair: bool = True) -> List[AuditResult]:
        """Perform comprehensive Git sovereign audit"""
        print("\n" + "="*80)
        print("🔍 GIT SOVEREIGN AUDIT")
        print("="*80)
        
        self.results = []
        
        # Check Git configuration
        self._check_git_config()
        
        # Check Git sovereign agent
        self._check_git_sovereign_agent()
        
        # Check Git hooks
        self._check_git_hooks()
        
        # Check .gitignore
        self._check_gitignore()
        
        # Check Git LFS if used
        self._check_git_lfs()
        
        # Check branch protection (if applicable)
        self._check_branch_status()
        
        # Check submodules
        self._check_submodules()
        
        # Auto-repair if requested
        if auto_repair:
            self._perform_repairs()
        
        self._print_results("GIT SOVEREIGN")
        return self.results
    
    def _check_git_config(self):
        """Check Git configuration"""
        try:
            # Check user.name
            result = subprocess.run(
                ["git", "config", "user.name"],
                cwd=self.repo_root,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0 and result.stdout.strip():
                self.results.append(AuditResult(
                    category="git_config",
                    check_name="user.name",
                    status="PASS",
                    message=f"Git user.name configured: {result.stdout.strip()}",
                    severity="INFO"
                ))
            else:
                self.results.append(AuditResult(
                    category="git_config",
                    check_name="user.name",
                    status="WARNING",
                    message="Git user.name not configured",
                    severity="LOW",
                    auto_repair_available=True
                ))
            
            # Check user.email
            result = subprocess.run(
                ["git", "config", "user.email"],
                cwd=self.repo_root,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0 and result.stdout.strip():
                self.results.append(AuditResult(
                    category="git_config",
                    check_name="user.email",
                    status="PASS",
                    message=f"Git user.email configured: {result.stdout.strip()}",
                    severity="INFO"
                ))
            else:
                self.results.append(AuditResult(
                    category="git_config",
                    check_name="user.email",
                    status="WARNING",
                    message="Git user.email not configured",
                    severity="LOW",
                    auto_repair_available=True
                ))
                
        except Exception as e:
            self.results.append(AuditResult(
                category="git_config",
                check_name="git_config_check",
                status="FAIL",
                message=f"Failed to check Git config: {e}",
                severity="MEDIUM"
            ))
    
    def _check_git_sovereign_agent(self):
        """Check Git sovereign agent installation"""
        agent_path = self.repo_root / "bridge_backend" / "bridge_core" / "agents" / "git_sovereign"
        
        if agent_path.exists():
            # Check for key files
            required_files = [
                "__init__.py",
                "manifest.py",
                "autonomy.py",
                "sdtf_integration.py",
                "brh_integration.py",
                "hxo_integration.py"
            ]
            
            missing_files = [f for f in required_files if not (agent_path / f).exists()]
            
            if not missing_files:
                self.results.append(AuditResult(
                    category="git_sovereign",
                    check_name="agent_installation",
                    status="PASS",
                    message="Git Sovereign Agent fully installed",
                    details={"files_checked": len(required_files)},
                    severity="INFO"
                ))
            else:
                self.results.append(AuditResult(
                    category="git_sovereign",
                    check_name="agent_installation",
                    status="WARNING",
                    message=f"Git Sovereign Agent missing files: {', '.join(missing_files)}",
                    details={"missing_files": missing_files},
                    severity="MEDIUM",
                    auto_repair_available=False
                ))
        else:
            self.results.append(AuditResult(
                category="git_sovereign",
                check_name="agent_installation",
                status="FAIL",
                message="Git Sovereign Agent not found",
                severity="HIGH",
                auto_repair_available=False
            ))
    
    def _check_git_hooks(self):
        """Check Git hooks"""
        hooks_dir = self.repo_root / ".git" / "hooks"
        
        if hooks_dir.exists():
            hooks = list(hooks_dir.glob("*"))
            hook_names = [h.name for h in hooks if h.is_file() and not h.name.endswith('.sample')]
            
            self.results.append(AuditResult(
                category="git_hooks",
                check_name="hooks_present",
                status="PASS" if hook_names else "WARNING",
                message=f"Git hooks found: {len(hook_names)}" if hook_names else "No Git hooks configured",
                details={"hooks": hook_names},
                severity="INFO"
            ))
        else:
            self.results.append(AuditResult(
                category="git_hooks",
                check_name="hooks_directory",
                status="WARNING",
                message="Git hooks directory not found",
                severity="LOW"
            ))
    
    def _check_gitignore(self):
        """Check .gitignore file"""
        gitignore_path = self.repo_root / ".gitignore"
        
        if gitignore_path.exists():
            content = gitignore_path.read_text()
            
            # Check for critical patterns
            critical_patterns = [
                "*.env",
                "__pycache__",
                "node_modules",
                ".DS_Store"
            ]
            
            missing_patterns = [p for p in critical_patterns if p not in content]
            
            if not missing_patterns:
                self.results.append(AuditResult(
                    category="git_ignore",
                    check_name="gitignore_complete",
                    status="PASS",
                    message=".gitignore contains critical patterns",
                    details={"checked_patterns": critical_patterns},
                    severity="INFO"
                ))
            else:
                self.results.append(AuditResult(
                    category="git_ignore",
                    check_name="gitignore_complete",
                    status="WARNING",
                    message=f".gitignore missing patterns: {', '.join(missing_patterns)}",
                    details={"missing_patterns": missing_patterns},
                    severity="MEDIUM",
                    auto_repair_available=True
                ))
        else:
            self.results.append(AuditResult(
                category="git_ignore",
                check_name="gitignore_exists",
                status="FAIL",
                message=".gitignore file not found",
                severity="HIGH",
                auto_repair_available=True
            ))
    
    def _check_git_lfs(self):
        """Check Git LFS configuration"""
        try:
            result = subprocess.run(
                ["git", "lfs", "env"],
                cwd=self.repo_root,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.results.append(AuditResult(
                    category="git_lfs",
                    check_name="lfs_configured",
                    status="PASS",
                    message="Git LFS is configured",
                    severity="INFO"
                ))
            else:
                self.results.append(AuditResult(
                    category="git_lfs",
                    check_name="lfs_configured",
                    status="WARNING",
                    message="Git LFS not configured (may not be needed)",
                    severity="LOW"
                ))
        except FileNotFoundError:
            self.results.append(AuditResult(
                category="git_lfs",
                check_name="lfs_installed",
                status="WARNING",
                message="Git LFS not installed (may not be needed)",
                severity="LOW"
            ))
    
    def _check_branch_status(self):
        """Check current branch status"""
        try:
            # Get current branch
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=self.repo_root,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                branch = result.stdout.strip()
                self.results.append(AuditResult(
                    category="git_branch",
                    check_name="current_branch",
                    status="PASS",
                    message=f"Current branch: {branch}",
                    details={"branch": branch},
                    severity="INFO"
                ))
                
                # Check if working tree is clean
                result = subprocess.run(
                    ["git", "status", "--porcelain"],
                    cwd=self.repo_root,
                    capture_output=True,
                    text=True
                )
                
                if not result.stdout.strip():
                    self.results.append(AuditResult(
                        category="git_branch",
                        check_name="working_tree_clean",
                        status="PASS",
                        message="Working tree is clean",
                        severity="INFO"
                    ))
                else:
                    modified_files = len(result.stdout.strip().split('\n'))
                    self.results.append(AuditResult(
                        category="git_branch",
                        check_name="working_tree_clean",
                        status="WARNING",
                        message=f"Working tree has {modified_files} modified files",
                        details={"modified_count": modified_files},
                        severity="LOW"
                    ))
        except Exception as e:
            self.results.append(AuditResult(
                category="git_branch",
                check_name="branch_status",
                status="FAIL",
                message=f"Failed to check branch status: {e}",
                severity="MEDIUM"
            ))
    
    def _check_submodules(self):
        """Check Git submodules"""
        gitmodules_path = self.repo_root / ".gitmodules"
        
        if gitmodules_path.exists():
            try:
                result = subprocess.run(
                    ["git", "submodule", "status"],
                    cwd=self.repo_root,
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    submodules = [line for line in result.stdout.split('\n') if line.strip()]
                    self.results.append(AuditResult(
                        category="git_submodules",
                        check_name="submodules_status",
                        status="PASS",
                        message=f"Submodules initialized: {len(submodules)}",
                        details={"count": len(submodules)},
                        severity="INFO"
                    ))
            except Exception as e:
                self.results.append(AuditResult(
                    category="git_submodules",
                    check_name="submodules_check",
                    status="WARNING",
                    message=f"Failed to check submodules: {e}",
                    severity="LOW"
                ))
        else:
            self.results.append(AuditResult(
                category="git_submodules",
                check_name="submodules_file",
                status="PASS",
                message="No submodules configured",
                severity="INFO"
            ))
    
    def _perform_repairs(self):
        """Perform auto-repairs for failed checks"""
        print("\n🔧 Performing auto-repairs...")
        
        for result in self.results:
            if result.auto_repair_available and result.status in ["FAIL", "WARNING"]:
                if result.check_name == "gitignore_complete":
                    self._repair_gitignore(result)
    
    def _repair_gitignore(self, result: AuditResult):
        """Repair .gitignore file"""
        try:
            gitignore_path = self.repo_root / ".gitignore"
            missing_patterns = result.details.get("missing_patterns", [])
            
            if missing_patterns:
                with open(gitignore_path, 'a') as f:
                    f.write("\n# Auto-added by Sovereign Audit\n")
                    for pattern in missing_patterns:
                        f.write(f"{pattern}\n")
                
                result.status = "REPAIRED"
                result.repaired = True
                result.message = f"Added missing patterns to .gitignore: {', '.join(missing_patterns)}"
                print(f"  ✅ Repaired: {result.check_name}")
        except Exception as e:
            print(f"  ❌ Failed to repair {result.check_name}: {e}")
    
    def _print_results(self, audit_name: str):
        """Print audit results summary"""
        pass_count = sum(1 for r in self.results if r.status == "PASS")
        fail_count = sum(1 for r in self.results if r.status == "FAIL")
        warning_count = sum(1 for r in self.results if r.status == "WARNING")
        repaired_count = sum(1 for r in self.results if r.status == "REPAIRED")
        
        print(f"\n📊 {audit_name} Results:")
        print(f"  ✅ PASS: {pass_count}")
        print(f"  ⚠️  WARNING: {warning_count}")
        print(f"  ❌ FAIL: {fail_count}")
        print(f"  🔧 REPAIRED: {repaired_count}")


class SovereignNetlifyAuditor:
    """Audits and repairs Netlify sovereign configuration"""
    
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.results: List[AuditResult] = []
    
    def audit(self, auto_repair: bool = True) -> List[AuditResult]:
        """Perform comprehensive Netlify sovereign audit"""
        print("\n" + "="*80)
        print("🌐 NETLIFY SOVEREIGN AUDIT")
        print("="*80)
        
        self.results = []
        
        # Check netlify.toml
        self._check_netlify_toml()
        
        # Check Netlify environment files
        self._check_netlify_env_files()
        
        # Check Netlify functions
        self._check_netlify_functions()
        
        # Check Netlify redirects
        self._check_netlify_redirects()
        
        # Check Netlify headers
        self._check_netlify_headers()
        
        # Check Netlify build scripts
        self._check_netlify_build_scripts()
        
        # Auto-repair if requested
        if auto_repair:
            self._perform_repairs()
        
        self._print_results("NETLIFY SOVEREIGN")
        return self.results
    
    def _check_netlify_toml(self):
        """Check netlify.toml configuration"""
        toml_path = self.repo_root / "netlify.toml"
        
        if toml_path.exists():
            content = toml_path.read_text()
            
            # Check for required sections
            required_sections = ["[build]", "[[headers]]"]
            missing_sections = [s for s in required_sections if s not in content]
            
            if not missing_sections:
                self.results.append(AuditResult(
                    category="netlify_config",
                    check_name="toml_complete",
                    status="PASS",
                    message="netlify.toml contains required sections",
                    details={"sections": required_sections},
                    severity="INFO"
                ))
            else:
                self.results.append(AuditResult(
                    category="netlify_config",
                    check_name="toml_complete",
                    status="WARNING",
                    message=f"netlify.toml missing sections: {', '.join(missing_sections)}",
                    details={"missing_sections": missing_sections},
                    severity="MEDIUM",
                    auto_repair_available=True
                ))
            
            # Check for security headers
            security_headers = [
                "X-Frame-Options",
                "X-Content-Type-Options",
                "Strict-Transport-Security"
            ]
            
            missing_headers = [h for h in security_headers if h not in content]
            
            if not missing_headers:
                self.results.append(AuditResult(
                    category="netlify_security",
                    check_name="security_headers",
                    status="PASS",
                    message="Security headers configured",
                    details={"headers": security_headers},
                    severity="INFO"
                ))
            else:
                self.results.append(AuditResult(
                    category="netlify_security",
                    check_name="security_headers",
                    status="WARNING",
                    message=f"Missing security headers: {', '.join(missing_headers)}",
                    details={"missing_headers": missing_headers},
                    severity="HIGH",
                    auto_repair_available=True
                ))
        else:
            self.results.append(AuditResult(
                category="netlify_config",
                check_name="toml_exists",
                status="FAIL",
                message="netlify.toml not found",
                severity="CRITICAL",
                auto_repair_available=True
            ))
    
    def _check_netlify_env_files(self):
        """Check Netlify environment files"""
        env_files = [
            ".env.netlify",
            ".env.netlify.example"
        ]
        
        for env_file in env_files:
            env_path = self.repo_root / env_file
            
            if env_path.exists():
                content = env_path.read_text()
                
                # Check for FORGE_DOMINION references
                if "FORGE_DOMINION" in content:
                    self.results.append(AuditResult(
                        category="netlify_env",
                        check_name=f"{env_file}_forge",
                        status="PASS",
                        message=f"{env_file} contains FORGE_DOMINION configuration",
                        severity="INFO"
                    ))
                else:
                    self.results.append(AuditResult(
                        category="netlify_env",
                        check_name=f"{env_file}_forge",
                        status="WARNING",
                        message=f"{env_file} missing FORGE_DOMINION configuration",
                        severity="MEDIUM",
                        auto_repair_available=True
                    ))
            else:
                is_example = env_file.endswith(".example")
                self.results.append(AuditResult(
                    category="netlify_env",
                    check_name=f"{env_file}_exists",
                    status="WARNING" if is_example else "FAIL",
                    message=f"{env_file} not found",
                    severity="LOW" if is_example else "HIGH",
                    auto_repair_available=True
                ))
    
    def _check_netlify_functions(self):
        """Check Netlify functions directory"""
        functions_dir = self.repo_root / "netlify" / "functions"
        
        if functions_dir.exists():
            functions = list(functions_dir.glob("*.js")) + list(functions_dir.glob("*.ts"))
            
            self.results.append(AuditResult(
                category="netlify_functions",
                check_name="functions_present",
                status="PASS",
                message=f"Netlify functions found: {len(functions)}",
                details={"count": len(functions), "functions": [f.name for f in functions]},
                severity="INFO"
            ))
        else:
            self.results.append(AuditResult(
                category="netlify_functions",
                check_name="functions_directory",
                status="WARNING",
                message="Netlify functions directory not found",
                severity="LOW"
            ))
    
    def _check_netlify_redirects(self):
        """Check Netlify redirects file"""
        redirects_path = self.repo_root / "_redirects"
        
        if redirects_path.exists():
            content = redirects_path.read_text()
            lines = [line.strip() for line in content.split('\n') if line.strip() and not line.startswith('#')]
            
            self.results.append(AuditResult(
                category="netlify_redirects",
                check_name="redirects_configured",
                status="PASS",
                message=f"Redirects configured: {len(lines)} rules",
                details={"rule_count": len(lines)},
                severity="INFO"
            ))
        else:
            self.results.append(AuditResult(
                category="netlify_redirects",
                check_name="redirects_exists",
                status="WARNING",
                message="_redirects file not found",
                severity="LOW"
            ))
    
    def _check_netlify_headers(self):
        """Check Netlify headers file"""
        headers_path = self.repo_root / "_headers"
        
        if headers_path.exists():
            content = headers_path.read_text()
            
            self.results.append(AuditResult(
                category="netlify_headers",
                check_name="headers_configured",
                status="PASS",
                message="_headers file configured",
                severity="INFO"
            ))
        else:
            self.results.append(AuditResult(
                category="netlify_headers",
                check_name="headers_exists",
                status="WARNING",
                message="_headers file not found (may be configured in netlify.toml)",
                severity="LOW"
            ))
    
    def _check_netlify_build_scripts(self):
        """Check Netlify build scripts"""
        scripts_dir = self.repo_root / "scripts"
        
        if scripts_dir.exists():
            netlify_scripts = list(scripts_dir.glob("netlify_*.sh")) + list(scripts_dir.glob("netlify_*.py"))
            
            if netlify_scripts:
                self.results.append(AuditResult(
                    category="netlify_build",
                    check_name="build_scripts",
                    status="PASS",
                    message=f"Netlify build scripts found: {len(netlify_scripts)}",
                    details={"scripts": [s.name for s in netlify_scripts]},
                    severity="INFO"
                ))
            else:
                self.results.append(AuditResult(
                    category="netlify_build",
                    check_name="build_scripts",
                    status="WARNING",
                    message="No Netlify build scripts found",
                    severity="LOW"
                ))
    
    def _perform_repairs(self):
        """Perform auto-repairs for failed checks"""
        print("\n🔧 Performing auto-repairs...")
        
        for result in self.results:
            if result.auto_repair_available and result.status in ["FAIL", "WARNING"]:
                # Currently no auto-repairs implemented for Netlify
                # These would require careful consideration
                pass
    
    def _print_results(self, audit_name: str):
        """Print audit results summary"""
        pass_count = sum(1 for r in self.results if r.status == "PASS")
        fail_count = sum(1 for r in self.results if r.status == "FAIL")
        warning_count = sum(1 for r in self.results if r.status == "WARNING")
        repaired_count = sum(1 for r in self.results if r.status == "REPAIRED")
        
        print(f"\n📊 {audit_name} Results:")
        print(f"  ✅ PASS: {pass_count}")
        print(f"  ⚠️  WARNING: {warning_count}")
        print(f"  ❌ FAIL: {fail_count}")
        print(f"  🔧 REPAIRED: {repaired_count}")


class SovereignRepositoryAuditor:
    """Audits and repairs repository integrity"""
    
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.results: List[AuditResult] = []
    
    def audit(self, auto_repair: bool = True) -> List[AuditResult]:
        """Perform comprehensive repository audit"""
        print("\n" + "="*80)
        print("📦 REPOSITORY SOVEREIGN AUDIT")
        print("="*80)
        
        self.results = []
        
        # Check repository structure
        self._check_repo_structure()
        
        # Check dependencies
        self._check_dependencies()
        
        # Check configuration files
        self._check_config_files()
        
        # Check documentation
        self._check_documentation()
        
        # Check security files
        self._check_security_files()
        
        # Check CI/CD workflows
        self._check_workflows()
        
        # Auto-repair if requested
        if auto_repair:
            self._perform_repairs()
        
        self._print_results("REPOSITORY SOVEREIGN")
        return self.results
    
    def _check_repo_structure(self):
        """Check repository structure"""
        required_dirs = [
            "bridge_backend",
            "bridge-frontend",
            "scripts",
            "docs"
        ]
        
        missing_dirs = [d for d in required_dirs if not (self.repo_root / d).exists()]
        
        if not missing_dirs:
            self.results.append(AuditResult(
                category="repo_structure",
                check_name="required_directories",
                status="PASS",
                message="All required directories present",
                details={"directories": required_dirs},
                severity="INFO"
            ))
        else:
            self.results.append(AuditResult(
                category="repo_structure",
                check_name="required_directories",
                status="WARNING",
                message=f"Missing directories: {', '.join(missing_dirs)}",
                details={"missing": missing_dirs},
                severity="MEDIUM"
            ))
    
    def _check_dependencies(self):
        """Check dependency files"""
        dep_files = {
            "Python": ["requirements.txt", "bridge_backend/pyproject.toml"],
            "Node.js": ["bridge-frontend/package.json"]
        }
        
        for lang, files in dep_files.items():
            for dep_file in files:
                dep_path = self.repo_root / dep_file
                
                if dep_path.exists():
                    self.results.append(AuditResult(
                        category="dependencies",
                        check_name=f"{lang}_deps",
                        status="PASS",
                        message=f"{lang} dependencies file found: {dep_file}",
                        severity="INFO"
                    ))
                else:
                    self.results.append(AuditResult(
                        category="dependencies",
                        check_name=f"{lang}_deps",
                        status="WARNING",
                        message=f"{lang} dependencies file missing: {dep_file}",
                        severity="MEDIUM"
                    ))
    
    def _check_config_files(self):
        """Check configuration files"""
        config_files = [
            "README.md",
            ".gitignore",
            ".env.example"
        ]
        
        for config_file in config_files:
            config_path = self.repo_root / config_file
            
            if config_path.exists():
                self.results.append(AuditResult(
                    category="config_files",
                    check_name=config_file,
                    status="PASS",
                    message=f"Configuration file present: {config_file}",
                    severity="INFO"
                ))
            else:
                severity = "HIGH" if config_file == "README.md" else "MEDIUM"
                self.results.append(AuditResult(
                    category="config_files",
                    check_name=config_file,
                    status="WARNING",
                    message=f"Configuration file missing: {config_file}",
                    severity=severity
                ))
    
    def _check_documentation(self):
        """Check documentation"""
        docs_dir = self.repo_root / "docs"
        
        if docs_dir.exists():
            doc_files = list(docs_dir.rglob("*.md"))
            
            self.results.append(AuditResult(
                category="documentation",
                check_name="docs_present",
                status="PASS",
                message=f"Documentation files found: {len(doc_files)}",
                details={"count": len(doc_files)},
                severity="INFO"
            ))
        else:
            self.results.append(AuditResult(
                category="documentation",
                check_name="docs_directory",
                status="WARNING",
                message="Documentation directory not found",
                severity="MEDIUM"
            ))
    
    def _check_security_files(self):
        """Check security files"""
        security_files = [
            "SECURITY.md",
            "SECURITY_AUDIT_SUMMARY.md"
        ]
        
        found_files = [f for f in security_files if (self.repo_root / f).exists()]
        
        if found_files:
            self.results.append(AuditResult(
                category="security",
                check_name="security_docs",
                status="PASS",
                message=f"Security documentation found: {', '.join(found_files)}",
                details={"files": found_files},
                severity="INFO"
            ))
        else:
            self.results.append(AuditResult(
                category="security",
                check_name="security_docs",
                status="WARNING",
                message="No security documentation found",
                severity="MEDIUM"
            ))
    
    def _check_workflows(self):
        """Check GitHub Actions workflows"""
        workflows_dir = self.repo_root / ".github" / "workflows"
        
        if workflows_dir.exists():
            workflows = list(workflows_dir.glob("*.yml")) + list(workflows_dir.glob("*.yaml"))
            
            self.results.append(AuditResult(
                category="ci_cd",
                check_name="workflows",
                status="PASS",
                message=f"GitHub Actions workflows found: {len(workflows)}",
                details={"count": len(workflows), "workflows": [w.name for w in workflows]},
                severity="INFO"
            ))
        else:
            self.results.append(AuditResult(
                category="ci_cd",
                check_name="workflows_directory",
                status="WARNING",
                message="GitHub Actions workflows directory not found",
                severity="LOW"
            ))
    
    def _perform_repairs(self):
        """Perform auto-repairs for failed checks"""
        print("\n🔧 Performing auto-repairs...")
        # Currently no auto-repairs implemented
        pass
    
    def _print_results(self, audit_name: str):
        """Print audit results summary"""
        pass_count = sum(1 for r in self.results if r.status == "PASS")
        fail_count = sum(1 for r in self.results if r.status == "FAIL")
        warning_count = sum(1 for r in self.results if r.status == "WARNING")
        repaired_count = sum(1 for r in self.results if r.status == "REPAIRED")
        
        print(f"\n📊 {audit_name} Results:")
        print(f"  ✅ PASS: {pass_count}")
        print(f"  ⚠️  WARNING: {warning_count}")
        print(f"  ❌ FAIL: {fail_count}")
        print(f"  🔧 REPAIRED: {repaired_count}")


class SovereignAuditOrchestrator:
    """Orchestrates all sovereign audits and repairs"""
    
    def __init__(self, repo_root: str = "."):
        self.repo_root = Path(repo_root).resolve()
        self.timestamp = datetime.now(timezone.utc)
        
        # Get Git info
        self.repo_info = self._get_repo_info()
        
        print("\n" + "="*80)
        print("👑 SOVEREIGN AUDIT & REPAIR ORCHESTRATOR")
        print("="*80)
        print(f"Repository: {self.repo_info['repository']}")
        print(f"Branch: {self.repo_info['branch']}")
        print(f"Commit: {self.repo_info['commit']}")
        print(f"Timestamp: {self.timestamp.isoformat()}")
        print("="*80)
    
    def _get_repo_info(self) -> Dict[str, str]:
        """Get repository information"""
        info = {
            "repository": "unknown",
            "branch": "unknown",
            "commit": "unknown"
        }
        
        try:
            # Get repository name
            result = subprocess.run(
                ["git", "config", "--get", "remote.origin.url"],
                cwd=self.repo_root,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                url = result.stdout.strip()
                if "/" in url:
                    info["repository"] = url.split("/")[-1].replace(".git", "")
            
            # Get current branch
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=self.repo_root,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                info["branch"] = result.stdout.strip()
            
            # Get current commit
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=self.repo_root,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                info["commit"] = result.stdout.strip()[:8]
        except Exception:
            pass
        
        return info
    
    def execute_full_audit(self, auto_repair: bool = True) -> AuditReport:
        """Execute full sovereign audit"""
        print("\n🚀 EXECUTING FULL SOVEREIGN AUDIT")
        
        all_results = []
        repair_actions = []
        
        # Git Sovereign Audit
        git_auditor = SovereignGitAuditor(self.repo_root)
        git_results = git_auditor.audit(auto_repair=auto_repair)
        all_results.extend(git_results)
        
        # Netlify Sovereign Audit
        netlify_auditor = SovereignNetlifyAuditor(self.repo_root)
        netlify_results = netlify_auditor.audit(auto_repair=auto_repair)
        all_results.extend(netlify_results)
        
        # Repository Sovereign Audit
        repo_auditor = SovereignRepositoryAuditor(self.repo_root)
        repo_results = repo_auditor.audit(auto_repair=auto_repair)
        all_results.extend(repo_results)
        
        # Collect repair actions
        repair_actions = [
            {
                "category": r.category,
                "check_name": r.check_name,
                "action": r.message
            }
            for r in all_results if r.repaired
        ]
        
        # Generate summary
        summary = self._generate_summary(all_results, repair_actions)
        
        # Create report
        report = AuditReport(
            timestamp=self.timestamp.isoformat(),
            repository=self.repo_info["repository"],
            branch=self.repo_info["branch"],
            commit_hash=self.repo_info["commit"],
            audits_performed=["git_sovereign", "netlify_sovereign", "repository_sovereign"],
            results=all_results,
            summary=summary,
            repair_actions=repair_actions
        )
        
        # Save report
        self._save_report(report)
        
        # Print final summary
        self._print_final_summary(report)
        
        return report
    
    def _generate_summary(self, results: List[AuditResult], repairs: List[Dict]) -> Dict[str, Any]:
        """Generate audit summary"""
        total = len(results)
        pass_count = sum(1 for r in results if r.status == "PASS")
        warning_count = sum(1 for r in results if r.status == "WARNING")
        fail_count = sum(1 for r in results if r.status == "FAIL")
        repaired_count = sum(1 for r in results if r.status == "REPAIRED")
        
        # Calculate score
        score = ((pass_count + repaired_count) / total * 100) if total > 0 else 0
        
        # Determine overall status
        if fail_count > 0:
            status = "NEEDS_ATTENTION"
        elif warning_count > 3:
            status = "WARNING"
        else:
            status = "HEALTHY"
        
        # Count by severity
        severity_counts = {}
        for r in results:
            severity_counts[r.severity] = severity_counts.get(r.severity, 0) + 1
        
        return {
            "total_checks": total,
            "passed": pass_count,
            "warnings": warning_count,
            "failed": fail_count,
            "repaired": repaired_count,
            "score": round(score, 2),
            "status": status,
            "severity_counts": severity_counts,
            "repair_actions_taken": len(repairs)
        }
    
    def _save_report(self, report: AuditReport):
        """Save audit report to file"""
        reports_dir = self.repo_root / "bridge_backend" / "diagnostics"
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        # Save latest report
        latest_path = reports_dir / "sovereign_audit_latest.json"
        with open(latest_path, 'w') as f:
            # Convert results to dicts
            report_dict = {
                "timestamp": report.timestamp,
                "repository": report.repository,
                "branch": report.branch,
                "commit_hash": report.commit_hash,
                "audits_performed": report.audits_performed,
                "results": [asdict(r) for r in report.results],
                "summary": report.summary,
                "repair_actions": report.repair_actions
            }
            json.dump(report_dict, f, indent=2)
        
        print(f"\n💾 Report saved: {latest_path}")
        
        # Save timestamped report
        timestamp_str = self.timestamp.strftime("%Y%m%d_%H%M%S")
        timestamped_path = reports_dir / f"sovereign_audit_{timestamp_str}.json"
        with open(timestamped_path, 'w') as f:
            json.dump(report_dict, f, indent=2)
        
        print(f"💾 Timestamped report: {timestamped_path}")
    
    def _print_final_summary(self, report: AuditReport):
        """Print final audit summary"""
        print("\n" + "="*80)
        print("📊 FINAL AUDIT SUMMARY")
        print("="*80)
        print(f"Total Checks: {report.summary['total_checks']}")
        print(f"✅ Passed: {report.summary['passed']}")
        print(f"⚠️  Warnings: {report.summary['warnings']}")
        print(f"❌ Failed: {report.summary['failed']}")
        print(f"🔧 Repaired: {report.summary['repaired']}")
        print(f"\n🎯 Score: {report.summary['score']}%")
        print(f"📈 Status: {report.summary['status']}")
        
        if report.repair_actions:
            print(f"\n🔧 Repair Actions Taken: {len(report.repair_actions)}")
            for action in report.repair_actions:
                print(f"  - {action['category']}.{action['check_name']}: {action['action']}")
        
        print("\n" + "="*80)
        
        # Print recommendation
        if report.summary['status'] == "HEALTHY":
            print("✅ SOVEREIGN AUTHORITY CONFIRMED - Repository is in excellent condition!")
        elif report.summary['status'] == "WARNING":
            print("⚠️  SOVEREIGNTY OPERATIONAL - Some warnings present, review recommended")
        else:
            print("❌ SOVEREIGNTY REQUIRES ATTENTION - Critical issues detected, action required")
        
        print("="*80)


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Sovereign Audit & Repair Orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full audit with auto-repair
  python sovereign_audit_orchestrator.py
  
  # Run audit without auto-repair
  python sovereign_audit_orchestrator.py --no-repair
  
  # Run audit in specific directory
  python sovereign_audit_orchestrator.py --repo-root /path/to/repo
        """
    )
    
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Repository root directory (default: current directory)"
    )
    
    parser.add_argument(
        "--no-repair",
        action="store_true",
        help="Disable auto-repair functionality"
    )
    
    args = parser.parse_args()
    
    # Execute audit
    orchestrator = SovereignAuditOrchestrator(args.repo_root)
    report = orchestrator.execute_full_audit(auto_repair=not args.no_repair)
    
    # Exit with appropriate code
    if report.summary['status'] == "HEALTHY":
        sys.exit(0)
    elif report.summary['status'] == "WARNING":
        sys.exit(1)
    else:
        sys.exit(2)


if __name__ == "__main__":
    main()
