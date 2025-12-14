"""
ARIE Models - Data structures for autonomous repository integrity
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from enum import Enum
from datetime import datetime


class PolicyType(str, Enum):
    """Fix policy types - what ARIE is allowed to do"""
    LINT_ONLY = "LINT_ONLY"  # Report only, no changes
    SAFE_EDIT = "SAFE_EDIT"  # Safe automated fixes (comments, formatting)
    REFACTOR = "REFACTOR"    # Structural changes (imports, routes)
    ARCHIVE = "ARCHIVE"      # Move/delete files


class Severity(str, Enum):
    """Issue severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class Finding(BaseModel):
    """A single integrity issue discovered by an analyzer"""
    id: str = Field(..., description="Unique finding ID")
    analyzer: str = Field(..., description="Analyzer that found this issue")
    severity: Severity = Field(..., description="Issue severity")
    category: str = Field(..., description="Issue category (e.g., deprecated, stub, import)")
    file_path: str = Field(..., description="File containing the issue")
    line_number: Optional[int] = Field(None, description="Line number if applicable")
    description: str = Field(..., description="Human-readable issue description")
    code_snippet: Optional[str] = Field(None, description="Relevant code snippet")
    suggested_fix: Optional[str] = Field(None, description="Suggested fix")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class Plan(BaseModel):
    """Execution plan for fixing issues"""
    id: str = Field(..., description="Unique plan ID")
    policy: PolicyType = Field(..., description="Policy type for this plan")
    findings: List[Finding] = Field(default_factory=list, description="Findings to fix")
    actions: List[Dict[str, Any]] = Field(default_factory=list, description="Actions to perform")
    estimated_impact: str = Field(..., description="Impact assessment")
    requires_approval: bool = Field(default=False, description="Whether manual approval is needed")
    created_at: str = Field(..., description="Plan creation timestamp")


class Patch(BaseModel):
    """A recorded patch/fix application"""
    id: str = Field(..., description="Unique patch ID")
    plan_id: str = Field(..., description="Plan that generated this patch")
    timestamp: str = Field(..., description="When patch was applied")
    files_modified: List[str] = Field(default_factory=list, description="Files changed")
    diff: str = Field(..., description="Git-style diff of changes")
    backup_path: Optional[str] = Field(None, description="Backup location")
    certified: bool = Field(default=False, description="Truth Engine certification status")
    certificate_id: Optional[str] = Field(None, description="Truth certificate ID if certified")
    rollback_available: bool = Field(default=True, description="Whether rollback is available")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class Rollback(BaseModel):
    """Rollback operation record"""
    id: str = Field(..., description="Unique rollback ID")
    patch_id: str = Field(..., description="Patch being rolled back")
    timestamp: str = Field(..., description="When rollback was performed")
    success: bool = Field(..., description="Whether rollback succeeded")
    error: Optional[str] = Field(None, description="Error message if failed")
    restored_files: List[str] = Field(default_factory=list, description="Files restored")


class Summary(BaseModel):
    """Summary of an ARIE scan/fix run"""
    run_id: str = Field(..., description="Unique run ID")
    timestamp: str = Field(..., description="Run timestamp")
    policy: PolicyType = Field(..., description="Policy used")
    dry_run: bool = Field(..., description="Whether this was a dry run")
    findings_count: int = Field(..., description="Total findings")
    findings_by_severity: Dict[str, int] = Field(default_factory=dict, description="Findings by severity")
    findings_by_category: Dict[str, int] = Field(default_factory=dict, description="Findings by category")
    fixes_applied: int = Field(default=0, description="Number of fixes applied")
    fixes_failed: int = Field(default=0, description="Number of fixes that failed")
    certification_status: Optional[str] = Field(None, description="Truth certification status")
    duration_seconds: float = Field(..., description="Run duration")
    findings: List[Finding] = Field(default_factory=list, description="All findings")
    patches: List[Patch] = Field(default_factory=list, description="Patches applied")


class ARIEConfig(BaseModel):
    """ARIE configuration"""
    enabled: bool = Field(default=True, description="Whether ARIE is enabled")
    policy: PolicyType = Field(default=PolicyType.SAFE_EDIT, description="Default policy")
    auto_fix_on_deploy: bool = Field(default=False, description="Auto-fix after successful deploy")
    max_patch_backlog: int = Field(default=50, description="Maximum patches to keep in backlog")
    strict_rollback: bool = Field(default=True, description="Strict rollback mode")
    excluded_paths: List[str] = Field(default_factory=list, description="Paths to exclude from scanning")
    schedule_enabled: bool = Field(default=False, description="Enable scheduled autonomous runs")
    schedule_interval_hours: int = Field(default=12, description="Interval between scheduled runs in hours")
    run_on_deploy: bool = Field(default=True, description="Run ARIE on deploy.platform.success events")
    admiral_only_apply: bool = Field(default=True, description="Require Admiral permission to apply fixes")
    truth_mandatory: bool = Field(default=True, description="Require Truth Engine certification")
    enabled_analyzers: List[str] = Field(default_factory=list, description="Enabled analyzers (empty = all)")


class ScanRequest(BaseModel):
    """Request to run ARIE scan"""
    policy: PolicyType = Field(default=PolicyType.SAFE_EDIT, description="Policy to use")
    dry_run: bool = Field(default=True, description="Dry run mode")
    apply: bool = Field(default=False, description="Apply fixes immediately")
    paths: Optional[List[str]] = Field(None, description="Specific paths to scan")


class RollbackRequest(BaseModel):
    """Request to rollback a patch"""
    patch_id: str = Field(..., description="Patch ID to rollback")
    force: bool = Field(default=False, description="Force rollback even if risky")
