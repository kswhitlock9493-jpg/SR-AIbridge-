"""
ARIE Core Engine - Autonomous Repository Integrity Engine
Pipelines: discover → analyze → plan → fix → verify → report
"""

import os
import re
import json
import hashlib
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, UTC
from abc import ABC, abstractmethod

from .models import (
    Finding, Plan, Patch, Rollback, Summary, PolicyType, Severity, ARIEConfig
)


class Analyzer(ABC):
    """Base class for integrity analyzers"""
    
    @abstractmethod
    def name(self) -> str:
        """Analyzer name"""
        pass
    
    @abstractmethod
    def analyze(self, file_path: Path, content: str) -> List[Finding]:
        """Analyze file and return findings"""
        pass


class DatetimeDeprecatedAnalyzer(Analyzer):
    """Detects deprecated datetime.utcnow() usage"""
    
    def name(self) -> str:
        return "datetime_deprecated"
    
    def analyze(self, file_path: Path, content: str) -> List[Finding]:
        findings = []
        if not file_path.suffix == '.py':
            return findings
        
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if 'datetime.utcnow()' in line:
                findings.append(Finding(
                    id=f"{self.name()}_{file_path}_{i}",
                    analyzer=self.name(),
                    severity=Severity.MEDIUM,
                    category="deprecated",
                    file_path=str(file_path),
                    line_number=i,
                    description=f"Deprecated datetime.utcnow() usage at line {i}",
                    code_snippet=line.strip(),
                    suggested_fix="Replace with datetime.now(UTC)",
                    metadata={"line": line.strip()}
                ))
        
        return findings


class StubMarkerAnalyzer(Analyzer):
    """Detects TODO stub markers in generated clients"""
    
    def name(self) -> str:
        return "stub_marker"
    
    def analyze(self, file_path: Path, content: str) -> List[Finding]:
        findings = []
        
        # Only scan generated client files
        if 'auto_generated' not in str(file_path) and 'generated' not in str(file_path):
            return findings
        
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if 'TODO stub' in line or 'TODO: stub' in line:
                findings.append(Finding(
                    id=f"{self.name()}_{file_path}_{i}",
                    analyzer=self.name(),
                    severity=Severity.LOW,
                    category="stub",
                    file_path=str(file_path),
                    line_number=i,
                    description=f"Stub marker found at line {i}",
                    code_snippet=line.strip(),
                    suggested_fix="Remove TODO stub comment",
                    metadata={"line": line.strip()}
                ))
        
        return findings


class RouteRegistryAnalyzer(Analyzer):
    """Validates route import and registration integrity"""
    
    def name(self) -> str:
        return "route_registry"
    
    def analyze(self, file_path: Path, content: str) -> List[Finding]:
        findings = []
        
        # Only scan route files and main.py
        if 'routes' not in str(file_path) and file_path.name != 'main.py':
            return findings
        
        if not file_path.suffix == '.py':
            return findings
        
        lines = content.split('\n')
        
        # Check for router imports without include_router
        has_router_import = False
        has_include_router = False
        
        for line in lines:
            if 'from fastapi import' in line and 'APIRouter' in line:
                has_router_import = True
            if 'app.include_router' in line:
                has_include_router = True
        
        if has_router_import and not has_include_router and file_path.name == 'main.py':
            findings.append(Finding(
                id=f"{self.name()}_{file_path}_missing_registration",
                analyzer=self.name(),
                severity=Severity.HIGH,
                category="route_integrity",
                file_path=str(file_path),
                line_number=None,
                description="Router imported but not registered with app.include_router",
                code_snippet=None,
                suggested_fix="Add app.include_router() call for imported router"
            ))
        
        return findings


class ImportHealthAnalyzer(Analyzer):
    """Checks for missing or relocated import symbols"""
    
    def name(self) -> str:
        return "import_health"
    
    def analyze(self, file_path: Path, content: str) -> List[Finding]:
        findings = []
        
        if not file_path.suffix == '.py':
            return findings
        
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            # Check for common import issues
            if line.strip().startswith('import ') or line.strip().startswith('from '):
                # Check for relative imports that might be broken
                if 'from .' in line and '..' in line:
                    # Overly nested relative import
                    dots = line.split('from')[1].split('import')[0].count('.')
                    if dots > 3:
                        findings.append(Finding(
                            id=f"{self.name()}_{file_path}_{i}",
                            analyzer=self.name(),
                            severity=Severity.LOW,
                            category="import_health",
                            file_path=str(file_path),
                            line_number=i,
                            description=f"Overly nested relative import ({dots} levels) at line {i}",
                            code_snippet=line.strip(),
                            suggested_fix="Consider using absolute imports"
                        ))
        
        return findings


class ConfigSmellAnalyzer(Analyzer):
    """Detects ENV access without defaults or type guards"""
    
    def name(self) -> str:
        return "config_smell"
    
    def analyze(self, file_path: Path, content: str) -> List[Finding]:
        findings = []
        
        if not file_path.suffix == '.py':
            return findings
        
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            # Check for os.getenv without default
            if 'os.getenv(' in line or 'os.environ[' in line:
                # Check if has default value
                if 'os.getenv(' in line:
                    # Parse to see if default is provided
                    match = re.search(r'os\.getenv\(["\']([^"\']+)["\']\s*\)', line)
                    if match:
                        # No default provided
                        findings.append(Finding(
                            id=f"{self.name()}_{file_path}_{i}",
                            analyzer=self.name(),
                            severity=Severity.LOW,
                            category="config_smell",
                            file_path=str(file_path),
                            line_number=i,
                            description=f"ENV access without default at line {i}",
                            code_snippet=line.strip(),
                            suggested_fix="Add default value to os.getenv()"
                        ))
        
        return findings


class DuplicateFileAnalyzer(Analyzer):
    """Detects duplicate files using parcel engine logic"""
    
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.file_hashes: Dict[str, List[Path]] = {}
    
    def name(self) -> str:
        return "duplicate_file"
    
    def _calculate_hash(self, file_path: Path) -> Optional[str]:
        """Calculate SHA256 hash of file"""
        try:
            hasher = hashlib.sha256()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception:
            return None
    
    def scan_repository(self) -> List[Finding]:
        """Scan entire repository for duplicates"""
        findings = []
        
        # Excluded directories
        excluded = {'.git', '__pycache__', 'node_modules', 'dist', 'build', 
                   '.cache', 'venv', 'env', '.venv', 'vault', 'logs', '.arie'}
        
        # Scan all files
        for file_path in self.repo_root.rglob('*'):
            if not file_path.is_file():
                continue
            
            # Skip excluded directories
            if any(part in excluded for part in file_path.parts):
                continue
            
            # Skip very large files
            try:
                if file_path.stat().st_size > 5 * 1024 * 1024:
                    continue
            except:
                continue
            
            file_hash = self._calculate_hash(file_path)
            if file_hash:
                if file_hash not in self.file_hashes:
                    self.file_hashes[file_hash] = []
                self.file_hashes[file_hash].append(file_path)
        
        # Create findings for duplicates
        for file_hash, files in self.file_hashes.items():
            if len(files) > 1:
                # Skip __init__.py files (intentional duplicates)
                if all(f.name == '__init__.py' for f in files):
                    continue
                
                file_list = ', '.join(str(f.relative_to(self.repo_root)) for f in files)
                findings.append(Finding(
                    id=f"{self.name()}_{file_hash[:8]}",
                    analyzer=self.name(),
                    severity=Severity.LOW,
                    category="duplicate",
                    file_path=str(files[0].relative_to(self.repo_root)),
                    line_number=None,
                    description=f"Duplicate file found ({len(files)} copies): {file_list}",
                    code_snippet=None,
                    suggested_fix=f"Keep one copy, remove {len(files)-1} duplicate(s)",
                    metadata={"duplicates": [str(f.relative_to(self.repo_root)) for f in files]}
                ))
        
        return findings
    
    def analyze(self, file_path: Path, content: str) -> List[Finding]:
        # This analyzer works at repository level, not file level
        return []


class DeadFileAnalyzer(Analyzer):
    """Detects dead/unused verification scripts and old files"""
    
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
    
    def name(self) -> str:
        return "dead_file"
    
    def scan_repository(self) -> List[Finding]:
        """Scan repository for dead files"""
        findings = []
        
        # Patterns indicating dead files
        dead_patterns = [
            'verify_v196', 'verify_v197', 'validate_anchorhold', 
            'verify_autonomy_deployment', 'verify_autonomy_integration',
            'verify_communication', 'verify_netlify_build'
        ]
        
        for pattern in dead_patterns:
            matches = list(self.repo_root.glob(f'**/{pattern}*.py'))
            for match in matches:
                # Only flag if in root directory (not in active directories)
                if match.parent == self.repo_root:
                    findings.append(Finding(
                        id=f"{self.name()}_{match.name}",
                        analyzer=self.name(),
                        severity=Severity.LOW,
                        category="dead_file",
                        file_path=str(match.relative_to(self.repo_root)),
                        line_number=None,
                        description=f"Dead verification script: {match.name}",
                        code_snippet=None,
                        suggested_fix="Remove or archive this file"
                    ))
        
        return findings
    
    def analyze(self, file_path: Path, content: str) -> List[Finding]:
        # This analyzer works at repository level
        return []


class UnusedFileAnalyzer(Analyzer):
    """Detects unused imports and unreferenced files"""
    
    def name(self) -> str:
        return "unused_file"
    
    def analyze(self, file_path: Path, content: str) -> List[Finding]:
        findings = []
        
        if not file_path.suffix == '.py':
            return findings
        
        # Check for unused imports (simple heuristic)
        lines = content.split('\n')
        imports = []
        
        for i, line in enumerate(lines, 1):
            if line.strip().startswith('import ') or line.strip().startswith('from '):
                # Extract imported names
                if 'import' in line:
                    parts = line.split('import')
                    if len(parts) > 1:
                        imported = parts[1].strip().split(',')
                        for imp in imported:
                            imp_name = imp.strip().split(' as ')[0].strip()
                            # Check if this import is used elsewhere in the file
                            if content.count(imp_name) == 1:  # Only appears in import line
                                findings.append(Finding(
                                    id=f"{self.name()}_{file_path}_{i}",
                                    analyzer=self.name(),
                                    severity=Severity.LOW,
                                    category="unused_import",
                                    file_path=str(file_path),
                                    line_number=i,
                                    description=f"Potentially unused import: {imp_name}",
                                    code_snippet=line.strip(),
                                    suggested_fix=f"Remove unused import {imp_name}"
                                ))
        
        return findings


class Fixer:
    """Base class for automated fixers"""
    
    def can_fix(self, finding: Finding) -> bool:
        """Check if this fixer can handle this finding"""
        return False
    
    def fix(self, file_path: Path, finding: Finding) -> Tuple[bool, Optional[str]]:
        """
        Apply fix to file
        Returns: (success, error_message)
        """
        return False, "Not implemented"


class DatetimeFixer(Fixer):
    """Fixes deprecated datetime.utcnow() calls"""
    
    def can_fix(self, finding: Finding) -> bool:
        return finding.analyzer == "datetime_deprecated"
    
    def fix(self, file_path: Path, finding: Finding) -> Tuple[bool, Optional[str]]:
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Replace datetime.utcnow() with datetime.now(UTC)
            modified = content.replace('datetime.utcnow()', 'datetime.now(UTC)')
            
            # Ensure UTC is imported
            if 'from datetime import' in modified:
                # Check if UTC is already imported
                if ', UTC' not in modified and 'import UTC' not in modified:
                    # Add UTC to imports
                    modified = modified.replace(
                        'from datetime import datetime',
                        'from datetime import datetime, UTC'
                    )
            
            if modified != content:
                file_path.write_text(modified, encoding='utf-8')
                return True, None
            
            return False, "No changes needed"
        except Exception as e:
            return False, str(e)


class StubCommentFixer(Fixer):
    """Removes TODO stub markers"""
    
    def can_fix(self, finding: Finding) -> bool:
        return finding.analyzer == "stub_marker"
    
    def fix(self, file_path: Path, finding: Finding) -> Tuple[bool, Optional[str]]:
        try:
            lines = file_path.read_text(encoding='utf-8').split('\n')
            
            if finding.line_number and 1 <= finding.line_number <= len(lines):
                line = lines[finding.line_number - 1]
                # Remove TODO stub comments
                line = re.sub(r'//\s*TODO\s*stub.*', '', line)
                line = re.sub(r'#\s*TODO\s*stub.*', '', line)
                line = re.sub(r'/\*\s*TODO\s*stub.*\*/', '', line)
                
                lines[finding.line_number - 1] = line
                
                file_path.write_text('\n'.join(lines), encoding='utf-8')
                return True, None
            
            return False, "Line number out of range"
        except Exception as e:
            return False, str(e)


class ImportAliasFixer(Fixer):
    """Fixes import alias issues"""
    
    def can_fix(self, finding: Finding) -> bool:
        return finding.analyzer == "import_health" and "relative import" in finding.description.lower()
    
    def fix(self, file_path: Path, finding: Finding) -> Tuple[bool, Optional[str]]:
        # This is a more complex fix that would require AST manipulation
        # For now, we'll skip it
        return False, "Automatic fix not available for this issue"


class ARIEEngine:
    """Main ARIE engine - orchestrates scanning, analysis, and fixing"""
    
    def __init__(self, repo_root: Optional[Path] = None, config: Optional[ARIEConfig] = None):
        self.repo_root = repo_root or Path.cwd()
        self.config = config or self._load_config()
        self.patch_dir = self.repo_root / "bridge_backend" / ".arie" / "patchlog"
        self.patch_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize analyzers
        self.analyzers: List[Analyzer] = [
            DatetimeDeprecatedAnalyzer(),
            StubMarkerAnalyzer(),
            RouteRegistryAnalyzer(),
            ImportHealthAnalyzer(),
            ConfigSmellAnalyzer(),
            DuplicateFileAnalyzer(self.repo_root),
            DeadFileAnalyzer(self.repo_root),
            UnusedFileAnalyzer(),
        ]
        
        # Initialize fixers
        self.fixers: List[Fixer] = [
            DatetimeFixer(),
            StubCommentFixer(),
            ImportAliasFixer(),
        ]
        
        self.last_summary: Optional[Summary] = None
    
    def _load_config(self) -> ARIEConfig:
        """Load configuration from environment"""
        return ARIEConfig(
            enabled=os.getenv("ARIE_ENABLED", "true").lower() == "true",
            policy=PolicyType(os.getenv("ARIE_POLICY", "SAFE_EDIT")),
            auto_fix_on_deploy=os.getenv("ARIE_AUTO_FIX_ON_DEPLOY_SUCCESS", "false").lower() == "true",
            max_patch_backlog=int(os.getenv("ARIE_MAX_PATCH_BACKLOG", "50")),
            strict_rollback=os.getenv("ARIE_STRICT_ROLLBACK", "true").lower() == "true",
        )
    
    def discover(self, paths: Optional[List[str]] = None) -> List[Path]:
        """Discover files to scan"""
        if paths:
            return [Path(p) for p in paths]
        
        # Scan entire repository
        files = []
        excluded = {'.git', '__pycache__', 'node_modules', 'dist', 'build',
                   '.cache', 'venv', 'env', '.venv', 'vault', 'logs', '.arie'}
        
        for file_path in self.repo_root.rglob('*'):
            if not file_path.is_file():
                continue
            
            # Skip excluded directories
            if any(part in excluded for part in file_path.parts):
                continue
            
            # Only scan code files
            if file_path.suffix in {'.py', '.js', '.ts', '.jsx', '.tsx', '.md'}:
                files.append(file_path)
        
        return files
    
    def analyze(self, files: List[Path]) -> List[Finding]:
        """Analyze files and collect findings"""
        all_findings = []
        
        # Run file-level analyzers
        for file_path in files:
            try:
                content = file_path.read_text(encoding='utf-8')
                
                for analyzer in self.analyzers:
                    findings = analyzer.analyze(file_path, content)
                    all_findings.extend(findings)
            except Exception as e:
                # Skip files that can't be read
                pass
        
        # Run repository-level analyzers
        for analyzer in self.analyzers:
            if hasattr(analyzer, 'scan_repository'):
                repo_findings = analyzer.scan_repository()
                all_findings.extend(repo_findings)
        
        return all_findings
    
    def plan(self, findings: List[Finding], policy: PolicyType) -> Plan:
        """Create execution plan from findings"""
        plan_id = f"plan_{datetime.now(UTC).isoformat()}_{hashlib.sha256(str(findings).encode()).hexdigest()[:8]}"
        
        # Filter findings based on policy
        planned_findings = []
        actions = []
        
        for finding in findings:
            if policy == PolicyType.LINT_ONLY:
                # No fixes, just report
                continue
            elif policy == PolicyType.SAFE_EDIT:
                # Only safe edits (comments, formatting, deprecated calls)
                if finding.category in ["deprecated", "stub", "config_smell"]:
                    planned_findings.append(finding)
                    actions.append({
                        "type": "fix",
                        "finding_id": finding.id,
                        "file": finding.file_path
                    })
            elif policy == PolicyType.REFACTOR:
                # Structural changes allowed
                if finding.category in ["deprecated", "stub", "import_health", "route_integrity"]:
                    planned_findings.append(finding)
                    actions.append({
                        "type": "fix",
                        "finding_id": finding.id,
                        "file": finding.file_path
                    })
            elif policy == PolicyType.ARCHIVE:
                # File operations allowed
                if finding.category in ["duplicate", "dead_file"]:
                    planned_findings.append(finding)
                    actions.append({
                        "type": "archive",
                        "finding_id": finding.id,
                        "file": finding.file_path
                    })
        
        impact = f"{len(planned_findings)} findings, {len(actions)} actions"
        
        return Plan(
            id=plan_id,
            policy=policy,
            findings=planned_findings,
            actions=actions,
            estimated_impact=impact,
            requires_approval=policy in [PolicyType.REFACTOR, PolicyType.ARCHIVE],
            created_at=datetime.now(UTC).isoformat() + "Z"
        )
    
    def fix(self, plan: Plan) -> Patch:
        """Execute plan and apply fixes"""
        patch_id = f"patch_{datetime.now(UTC).isoformat()}_{hashlib.sha256(plan.id.encode()).hexdigest()[:8]}"
        
        files_modified = []
        diff_parts = []
        
        for action in plan.actions:
            if action["type"] == "fix":
                # Find the finding
                finding = next((f for f in plan.findings if f.id == action["finding_id"]), None)
                if not finding:
                    continue
                
                # Find a fixer that can handle this
                file_path = self.repo_root / finding.file_path
                
                for fixer in self.fixers:
                    if fixer.can_fix(finding):
                        # Take backup
                        backup_content = file_path.read_text(encoding='utf-8') if file_path.exists() else ""
                        
                        # Apply fix
                        success, error = fixer.fix(file_path, finding)
                        
                        if success:
                            files_modified.append(finding.file_path)
                            # Create diff
                            new_content = file_path.read_text(encoding='utf-8')
                            diff_parts.append(f"--- {finding.file_path}\n+++ {finding.file_path}\n{backup_content[:100]}...\n--->\n{new_content[:100]}...")
                        
                        break
        
        patch = Patch(
            id=patch_id,
            plan_id=plan.id,
            timestamp=datetime.now(UTC).isoformat() + "Z",
            files_modified=files_modified,
            diff="\n".join(diff_parts),
            certified=False,
            rollback_available=True,
            metadata={"policy": plan.policy.value}
        )
        
        # Save patch to journal
        patch_file = self.patch_dir / f"{patch_id}.json"
        patch_file.write_text(json.dumps(patch.model_dump(), indent=2))
        
        return patch
    
    def verify(self, patch: Patch) -> bool:
        """Verify patch application (placeholder for Truth Engine integration)"""
        # This will be integrated with Truth Engine
        return len(patch.files_modified) > 0
    
    def report(self, findings: List[Finding], patches: List[Patch], policy: PolicyType, dry_run: bool, duration: float) -> Summary:
        """Generate summary report"""
        run_id = f"run_{datetime.now(UTC).isoformat()}_{hashlib.sha256(str(findings).encode()).hexdigest()[:8]}"
        
        # Count findings by severity
        by_severity = {}
        for finding in findings:
            sev = finding.severity.value
            by_severity[sev] = by_severity.get(sev, 0) + 1
        
        # Count findings by category
        by_category = {}
        for finding in findings:
            cat = finding.category
            by_category[cat] = by_category.get(cat, 0) + 1
        
        summary = Summary(
            run_id=run_id,
            timestamp=datetime.now(UTC).isoformat() + "Z",
            policy=policy,
            dry_run=dry_run,
            findings_count=len(findings),
            findings_by_severity=by_severity,
            findings_by_category=by_category,
            fixes_applied=sum(len(p.files_modified) for p in patches),
            fixes_failed=0,
            duration_seconds=duration,
            findings=findings,
            patches=patches
        )
        
        self.last_summary = summary
        return summary
    
    def run(self, policy: Optional[PolicyType] = None, dry_run: bool = True, 
            apply: bool = False, paths: Optional[List[str]] = None) -> Summary:
        """Main execution pipeline"""
        import time
        start_time = time.time()
        
        if not self.config.enabled:
            return Summary(
                run_id="disabled",
                timestamp=datetime.now(UTC).isoformat() + "Z",
                policy=PolicyType.LINT_ONLY,
                dry_run=True,
                findings_count=0,
                findings_by_severity={},
                findings_by_category={},
                duration_seconds=0.0,
                findings=[],
                patches=[]
            )
        
        policy = policy or self.config.policy
        
        # Pipeline: discover → analyze → plan → fix → verify → report
        files = self.discover(paths)
        findings = self.analyze(files)
        plan = self.plan(findings, policy)
        
        patches = []
        if apply and not dry_run:
            patch = self.fix(plan)
            verified = self.verify(patch)
            if verified:
                patches.append(patch)
        
        duration = time.time() - start_time
        summary = self.report(findings, patches, policy, dry_run, duration)
        
        return summary
    
    def rollback(self, patch_id: str, force: bool = False) -> Rollback:
        """Rollback a specific patch"""
        patch_file = self.patch_dir / f"{patch_id}.json"
        
        if not patch_file.exists():
            return Rollback(
                id=f"rollback_{patch_id}",
                patch_id=patch_id,
                timestamp=datetime.now(UTC).isoformat() + "Z",
                success=False,
                error="Patch not found"
            )
        
        # Load patch
        patch_data = json.loads(patch_file.read_text())
        patch = Patch(**patch_data)
        
        if not patch.rollback_available and not force:
            return Rollback(
                id=f"rollback_{patch_id}",
                patch_id=patch_id,
                timestamp=datetime.now(UTC).isoformat() + "Z",
                success=False,
                error="Rollback not available for this patch"
            )
        
        # Perform rollback using git
        try:
            restored = []
            for file_path in patch.files_modified:
                # Use git to restore
                result = subprocess.run(
                    ["git", "checkout", "HEAD~1", "--", file_path],
                    cwd=self.repo_root,
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    restored.append(file_path)
            
            return Rollback(
                id=f"rollback_{patch_id}",
                patch_id=patch_id,
                timestamp=datetime.now(UTC).isoformat() + "Z",
                success=True,
                restored_files=restored
            )
        except Exception as e:
            return Rollback(
                id=f"rollback_{patch_id}",
                patch_id=patch_id,
                timestamp=datetime.now(UTC).isoformat() + "Z",
                success=False,
                error=str(e)
            )
    
    def get_last_report(self) -> Optional[Summary]:
        """Get the last run summary"""
        return self.last_summary
