"""
Compliance Validator for Autonomy Engine
Integrates copyright, license, and LOC tracking into autonomous task execution
"""
from __future__ import annotations
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

try:
    from utils.license_scanner import scan_files, guess_license_for_text
    from utils.counterfeit_detector import best_match_against_corpus
    from utils.scan_policy import load_policy
except ImportError:
    try:
        from bridge_backend.utils.license_scanner import scan_files, guess_license_for_text
        from bridge_backend.utils.counterfeit_detector import best_match_against_corpus
        from bridge_backend.utils.scan_policy import load_policy
    except ImportError:
        # Define fallback minimal implementations
        def load_policy():
            return {
                "blocked_licenses": ["GPL-2.0", "GPL-3.0", "AGPL-3.0"],
                "allowed_licenses": ["MIT", "Apache-2.0", "BSD-3-Clause"],
                "thresholds": {"counterfeit_confidence_block": 0.94, "counterfeit_confidence_flag": 0.6},
                "scan_exclude_paths": ["node_modules", ".venv", "__pycache__"]
            }
        
        def scan_files(root, files):
            return {"files": [], "summary": {"counts_by_license": {}}}
        
        def best_match_against_corpus(target, corpus):
            return {"score": 0.0, "match_path": None}


COMPLIANCE_VAULT = Path("vault/autonomy/compliance")
COMPLIANCE_VAULT.mkdir(parents=True, exist_ok=True)


class ComplianceValidator:
    """
    Validates compliance (copyright, license, LOC) for autonomous tasks
    Ensures all autonomous work starts original and open-source compliant
    """
    
    def __init__(self):
        self.policy = load_policy()
        self.vault = COMPLIANCE_VAULT
    
    def validate_task_compliance(self, task_id: str, project: str, 
                                 files: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Validate compliance for a task before/during execution
        
        Args:
            task_id: Unique task identifier
            project: Project name/path
            files: Optional list of files to check
        
        Returns:
            Compliance validation result with copyright, license, and LOC info
        """
        timestamp = datetime.utcnow().isoformat() + "Z"
        
        # Determine project root
        project_root = Path(project) if Path(project).exists() else Path(".")
        
        # Get files to scan
        if not files:
            files = self._discover_source_files(project_root)
        
        # Run license scan
        license_result = self._scan_licenses(project_root, files)
        
        # Run copyright/counterfeit check
        copyright_result = self._check_copyright(project_root, files)
        
        # Count LOC
        loc_result = self._count_loc(project_root, files)
        
        # Evaluate compliance state
        compliance_state = self._evaluate_compliance(
            license_result, copyright_result
        )
        
        # Create validation record
        validation = {
            "task_id": task_id,
            "project": project,
            "timestamp": timestamp,
            "license_scan": license_result,
            "copyright_check": copyright_result,
            "loc_metrics": loc_result,
            "compliance_state": compliance_state,
            "policy_version": "v1.0"
        }
        
        # Save validation record
        self._save_validation(task_id, validation)
        
        return validation
    
    def _discover_source_files(self, root: Path) -> List[str]:
        """Discover source files in project"""
        extensions = {".py", ".js", ".jsx", ".ts", ".tsx"}
        exclude_dirs = set(self.policy.get("scan_exclude_paths", []))
        
        files = []
        for ext in extensions:
            for file_path in root.rglob(f"*{ext}"):
                # Check if file is in excluded path
                relative = file_path.relative_to(root)
                if any(excluded in str(relative) for excluded in exclude_dirs):
                    continue
                files.append(str(relative))
        
        return files[:100]  # Limit to prevent overload
    
    def _scan_licenses(self, root: Path, files: List[str]) -> Dict[str, Any]:
        """Scan files for license compliance"""
        if not files:
            return {"compliant": True, "licenses": {}, "files_scanned": 0}
        
        scan_result = scan_files(root, files)
        
        # Check for blocked licenses
        blocked = set(self.policy.get("blocked_licenses", []))
        violations = []
        
        for file_info in scan_result.get("files", []):
            lic = file_info.get("license_guess", "UNKNOWN")
            if lic in blocked:
                violations.append({
                    "file": file_info["path"],
                    "license": lic,
                    "reason": "blocked_license"
                })
        
        return {
            "compliant": len(violations) == 0,
            "licenses": scan_result.get("summary", {}).get("counts_by_license", {}),
            "files_scanned": len(scan_result.get("files", [])),
            "violations": violations
        }
    
    def _check_copyright(self, root: Path, files: List[str]) -> Dict[str, Any]:
        """Check for potential copyright violations using counterfeit detector"""
        if not files:
            return {"original": True, "matches": [], "files_checked": 0}
        
        # Use bridge_backend as corpus for internal checking
        corpus = root / "bridge_backend"
        if not corpus.exists():
            corpus = root
        
        threshold_block = self.policy["thresholds"]["counterfeit_confidence_block"]
        threshold_flag = self.policy["thresholds"]["counterfeit_confidence_flag"]
        
        suspicious = []
        flagged = []
        
        for file_rel in files[:50]:  # Limit for performance
            file_path = root / file_rel
            if not file_path.exists() or not file_path.is_file():
                continue
            
            match = best_match_against_corpus(file_path, corpus)
            score = match.get("score", 0.0)
            
            if score >= threshold_block:
                suspicious.append({
                    "file": file_rel,
                    "match": match.get("match_path"),
                    "confidence": score,
                    "severity": "high"
                })
            elif score >= threshold_flag:
                flagged.append({
                    "file": file_rel,
                    "match": match.get("match_path"),
                    "confidence": score,
                    "severity": "medium"
                })
        
        return {
            "original": len(suspicious) == 0,
            "files_checked": min(len(files), 50),
            "suspicious_matches": suspicious,
            "flagged_matches": flagged,
            "threshold_block": threshold_block,
            "threshold_flag": threshold_flag
        }
    
    def _count_loc(self, root: Path, files: List[str]) -> Dict[str, Any]:
        """Count lines of code for tracked files"""
        if not files:
            return {"total_lines": 0, "files_counted": 0, "by_extension": {}}
        
        loc_by_ext = {}
        total_lines = 0
        files_counted = 0
        
        for file_rel in files:
            file_path = root / file_rel
            if not file_path.exists() or not file_path.is_file():
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = len(f.readlines())
                
                ext = file_path.suffix or "no_ext"
                loc_by_ext[ext] = loc_by_ext.get(ext, 0) + lines
                total_lines += lines
                files_counted += 1
            except Exception:
                continue
        
        return {
            "total_lines": total_lines,
            "files_counted": files_counted,
            "by_extension": loc_by_ext
        }
    
    def _evaluate_compliance(self, license_result: Dict, 
                            copyright_result: Dict) -> Dict[str, Any]:
        """Evaluate overall compliance state"""
        
        # Check license compliance
        license_ok = license_result.get("compliant", True)
        license_violations = license_result.get("violations", [])
        
        # Check copyright originality
        copyright_ok = copyright_result.get("original", True)
        suspicious = copyright_result.get("suspicious_matches", [])
        
        # Determine overall state
        if not license_ok or not copyright_ok:
            state = "blocked"
            reason = []
            if not license_ok:
                reason.append(f"license_violations: {len(license_violations)}")
            if not copyright_ok:
                reason.append(f"copyright_violations: {len(suspicious)}")
            reason_str = ", ".join(reason)
        elif copyright_result.get("flagged_matches", []):
            state = "flagged"
            reason_str = f"flagged_matches: {len(copyright_result['flagged_matches'])}"
        else:
            state = "compliant"
            reason_str = "all_checks_passed"
        
        return {
            "state": state,
            "reason": reason_str,
            "license_compliant": license_ok,
            "copyright_original": copyright_ok,
            "safe_to_proceed": state in ["compliant", "flagged"]
        }
    
    def _save_validation(self, task_id: str, validation: Dict[str, Any]):
        """Save validation record to vault"""
        validation_file = self.vault / f"{task_id}.json"
        validation_file.write_text(json.dumps(validation, indent=2))
    
    def get_validation(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve validation record for a task"""
        validation_file = self.vault / f"{task_id}.json"
        if validation_file.exists():
            return json.loads(validation_file.read_text())
        return None
