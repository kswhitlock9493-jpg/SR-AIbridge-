from __future__ import annotations
import json, uuid, time
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

try:
    from .compliance_validator import ComplianceValidator
except ImportError:
    ComplianceValidator = None

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
    compliance_validation: Optional[Dict] = None  # Compliance check results

    def seal_path(self) -> Path:
        return VAULT / f"{self.id}.json"

class AutonomyEngine:
    def __init__(self, enable_compliance: bool = True):
        self._active: Dict[str, TaskContract] = {}
        self._compliance_enabled = enable_compliance and ComplianceValidator is not None
        self._validator = ComplianceValidator() if self._compliance_enabled else None

    def create_task(self, project: str, captain: str, objective: str,
                    permissions: Dict[str, Any], mode: str = "screen",
                    files: Optional[list] = None, 
                    validate_compliance: bool = True) -> TaskContract:
        tid = str(uuid.uuid4())
        
        # Run compliance validation if enabled
        compliance_result = None
        if self._compliance_enabled and validate_compliance:
            try:
                compliance_result = self._validator.validate_task_compliance(
                    task_id=tid,
                    project=project,
                    files=files
                )
            except Exception as e:
                # Log error but don't fail task creation
                compliance_result = {
                    "error": str(e),
                    "state": "error",
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }
        
        tc = TaskContract(
            id=tid,
            project=project,
            captain=captain,
            mode=mode,
            permissions=permissions,
            objective=objective,
            created_at=datetime.utcnow().isoformat() + "Z",
            compliance_validation=compliance_result
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

    def list_tasks(self) -> list[Dict]:
        return [asdict(t) for t in self._active.values()]
    
    def get_compliance_validation(self, task_id: str) -> Optional[Dict]:
        """Get compliance validation for a task"""
        tc = self._active.get(task_id)
        if tc:
            return tc.compliance_validation
        
        # Try to retrieve from validator vault if not in memory
        if self._validator:
            return self._validator.get_validation(task_id)
        
        return None
    
    def update_task_loc(self, task_id: str, loc_metrics: Dict[str, Any]) -> Optional[TaskContract]:
        """Update LOC metrics for a task"""
        tc = self._active.get(task_id)
        if not tc:
            return None
        
        # Add LOC metrics to compliance validation or create new one
        if not tc.compliance_validation:
            tc.compliance_validation = {}
        
        tc.compliance_validation["loc_metrics"] = loc_metrics
        tc.compliance_validation["loc_updated_at"] = datetime.utcnow().isoformat() + "Z"
        
        self._seal(tc)
        return tc