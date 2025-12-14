from __future__ import annotations
import json, uuid, time, os
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone

VAULT = Path("vault/autonomy")
VAULT.mkdir(parents=True, exist_ok=True)

@dataclass
class TaskContract:
    id: str
    project: str
    captain: str
    mode: str                 # "screen" | "connector" | "hybrid"
    permissions: Dict[str, Any]
    objective: str
    created_at: str
    status: str = "pending"   # pending | running | complete | failed
    result: Optional[Dict] = None
    # Compliance & Originality checks
    compliance_check: Optional[Dict] = None
    loc_metrics: Optional[Dict] = None
    originality_verified: bool = False

    def seal_path(self) -> Path:
        return VAULT / f"{self.id}.json"

class AutonomyEngine:
    def __init__(self):
        self._active: Dict[str, TaskContract] = {}

    def _check_compliance(self, project: str, files_to_scan: Optional[List[str]] = None) -> Dict:
        """
        Run compliance scan to ensure code originality and proper licensing.
        This is the anti-copyright engine integration.
        """
        try:
            from bridge_backend.utils.license_scanner import scan_files
            from bridge_backend.utils.counterfeit_detector import best_match_against_corpus
            from bridge_backend.utils.scan_policy import load_policy
        except ImportError:
            from utils.license_scanner import scan_files
            from utils.counterfeit_detector import best_match_against_corpus
            from utils.scan_policy import load_policy
        
        root = Path.cwd()
        policy = load_policy()
        
        # If no specific files provided, scan project directory
        if not files_to_scan:
            project_path = root / "bridge_backend" / "bridge_core" / "engines" / project
            if project_path.exists():
                files_to_scan = [str(p.relative_to(root)) for p in project_path.rglob("*.py")]
            else:
                files_to_scan = []
        
        # License scan
        lic = scan_files(root, files_to_scan) if files_to_scan else {"files": [], "summary": {"counts_by_license": {}}}
        
        # Counterfeit/clone detection
        cf = []
        corpus = root / "bridge_backend"
        for rel in files_to_scan:
            p = root / rel
            if not p.exists() or p.is_dir():
                continue
            if any(str(p).find(ex) >= 0 for ex in policy.get("scan_exclude_paths", [])):
                continue
            match = best_match_against_corpus(p, corpus)
            cf.append({"path": rel, **match})
        
        # Policy evaluation
        state = "ok"
        blocked = set(policy.get("blocked_licenses", []))
        for f in lic["files"]:
            if f["license_guess"] in blocked:
                state = "blocked"
                break
        
        if state != "blocked":
            max_hit = max((x["score"] for x in cf), default=0.0)
            block_threshold = policy.get("thresholds", {}).get("counterfeit_confidence_block", 0.94)
            flag_threshold = policy.get("thresholds", {}).get("counterfeit_confidence_flag", 0.60)
            
            if max_hit >= block_threshold:
                state = "blocked"
            elif max_hit >= flag_threshold:
                state = "flagged"
        
        return {
            "state": state,
            "license": lic,
            "counterfeit": cf,
            "timestamp": datetime.now(timezone.utc).isoformat() + "Z"
        }

    def _get_loc_metrics(self, project: str) -> Dict:
        """
        Get lines of code metrics for the project.
        This is the LOC engine integration.
        """
        root = Path.cwd()
        project_path = root / "bridge_backend" / "bridge_core" / "engines" / project
        
        if not project_path.exists():
            return {
                "total_lines": 0,
                "total_files": 0,
                "by_type": {},
                "timestamp": datetime.now(timezone.utc).isoformat() + "Z"
            }
        
        # Simple LOC counter for project
        total_lines = 0
        total_files = 0
        by_type = {}
        
        for p in project_path.rglob("*"):
            if p.is_file() and p.suffix in [".py", ".js", ".ts", ".jsx", ".tsx"]:
                try:
                    lines = len(p.read_text(encoding="utf-8", errors="ignore").splitlines())
                    total_lines += lines
                    total_files += 1
                    
                    ext = p.suffix
                    if ext not in by_type:
                        by_type[ext] = {"files": 0, "lines": 0}
                    by_type[ext]["files"] += 1
                    by_type[ext]["lines"] += lines
                except Exception:
                    continue
        
        return {
            "total_lines": total_lines,
            "total_files": total_files,
            "by_type": by_type,
            "timestamp": datetime.now(timezone.utc).isoformat() + "Z"
        }

    def create_task(self, project: str, captain: str, objective: str,
                    permissions: Dict[str, Any], mode: str = "screen",
                    verify_originality: bool = True,
                    files: Optional[List[str]] = None) -> TaskContract:
        """
        Create a new autonomy task with integrated compliance and LOC checks.
        
        Args:
            project: Project name
            captain: Task captain/owner
            objective: Task objective
            permissions: Permission dictionary
            mode: Task mode (screen/connector/hybrid)
            verify_originality: Run anti-copyright and compliance checks
            files: Optional list of specific files to scan for compliance
        
        Returns:
            TaskContract with compliance and LOC metrics
        """
        tid = str(uuid.uuid4())
        
        # Run compliance check (anti-copyright engine)
        compliance_check = None
        originality_verified = False
        if verify_originality:
            try:
                compliance_check = self._check_compliance(project, files)
                # Task is verified as original if state is "ok"
                originality_verified = compliance_check["state"] == "ok"
            except Exception as e:
                # Log error but don't block task creation
                compliance_check = {
                    "state": "error",
                    "error": str(e),
                    "timestamp": datetime.now(timezone.utc).isoformat() + "Z"
                }
        
        # Get LOC metrics
        loc_metrics = None
        try:
            loc_metrics = self._get_loc_metrics(project)
        except Exception as e:
            # Log error but don't block task creation
            loc_metrics = {
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat() + "Z"
            }
        
        tc = TaskContract(
            id=tid,
            project=project,
            captain=captain,
            mode=mode,
            permissions=permissions,
            objective=objective,
            created_at=datetime.now(timezone.utc).isoformat() + "Z",
            compliance_check=compliance_check,
            loc_metrics=loc_metrics,
            originality_verified=originality_verified
        )
        self._active[tid] = tc
        self._seal(tc)
        return tc

    def update_status(self, task_id: str, status: str, result: Optional[Dict]=None):
        tc = self._active.get(task_id)
        if not tc:
            return None
        tc.status = status
        tc.result = result
        self._seal(tc)
        return tc

    def _seal(self, tc: TaskContract):
        tc.seal_path().write_text(json.dumps(asdict(tc), indent=2))

    def get_compliance_validation(self, task_id: str) -> Optional[Dict]:
        """
        Get compliance validation results for a specific task.
        
        Args:
            task_id: Task ID
            
        Returns:
            Compliance validation dict or None if task not found
        """
        tc = self._active.get(task_id)
        if not tc:
            return None
        
        if not tc.compliance_check:
            return None
            
        # Return compliance state with safe_to_proceed flag
        compliance_state = {
            "state": tc.compliance_check.get("state", "unknown"),
            "safe_to_proceed": tc.compliance_check.get("state") in ["ok", "flagged"]
        }
        
        return {
            "compliance_state": compliance_state,
            "compliance_check": tc.compliance_check,
            "originality_verified": tc.originality_verified
        }
    
    def update_task_loc(self, task_id: str) -> Optional[Dict]:
        """
        Update LOC metrics for a specific task.
        
        Args:
            task_id: Task ID
            
        Returns:
            Updated LOC metrics or None if task not found
        """
        tc = self._active.get(task_id)
        if not tc:
            return None
        
        try:
            loc_metrics = self._get_loc_metrics(tc.project)
            tc.loc_metrics = loc_metrics
            self._seal(tc)
            return loc_metrics
        except Exception as e:
            return {
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat() + "Z"
            }

    def list_tasks(self) -> list[Dict]:
        return [asdict(t) for t in self._active.values()]