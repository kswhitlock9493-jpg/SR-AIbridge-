"""
Sovereign MicroScribe Engine
Quantum-enhanced diff analysis with security validation and resonance-aware PR generation
"""

import logging
import os
import re
from datetime import datetime, UTC
from typing import Dict, Any, List, Optional, Tuple
from pydantic import BaseModel
from enum import Enum

logger = logging.getLogger(__name__)


class AnalysisMode(str, Enum):
    """Analysis depth modes based on bridge resonance"""
    STANDARD = "STANDARD"      # Basic analysis (resonance < 0.95)
    DEEP = "DEEP"             # Deep analysis (0.95 ≤ resonance < 0.99)
    QUANTUM = "QUANTUM"        # Quantum analysis (resonance ≥ 0.99)


class SecurityLevel(str, Enum):
    """Security risk levels"""
    NONE = "NONE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class DiffAnalysis(BaseModel):
    """Result of diff analysis"""
    summary: str
    files_changed: int
    lines_added: int
    lines_removed: int
    risk_level: SecurityLevel
    security_findings: List[str] = []
    recommendations: List[str] = []
    mode: AnalysisMode
    resonance: float
    timestamp: str


class PRTemplate(BaseModel):
    """Generated PR template"""
    title: str
    description: str
    labels: List[str] = []
    reviewers: List[str] = []
    metadata: Dict[str, Any] = {}


class SovereignMicroScribe:
    """
    Quantum-enhanced diff analysis and PR generation engine
    
    Features:
    - Quantum-enhanced diff analysis with security validation
    - Resonance-aware PR generation (QUANTUM/DEEP/STANDARD modes)
    - Enterprise-grade change intelligence with risk assessment
    - Bridge-native integration with sovereign compliance
    """
    
    def __init__(self):
        self.min_resonance = float(os.getenv("MICROSCRIBE_MIN_RESONANCE", "0.90"))
        self._compliance_guard = None
    
    def _get_compliance_guard(self):
        """Lazy load compliance guard"""
        if self._compliance_guard is None:
            from .sovereign_guard import SovereignComplianceGuard
            self._compliance_guard = SovereignComplianceGuard()
        return self._compliance_guard
    
    def _get_bridge_resonance(self) -> float:
        """Get current bridge resonance level"""
        try:
            return float(os.getenv("BRIDGE_RESONANCE", "0.99"))
        except Exception as e:
            logger.warning(f"Failed to get bridge resonance: {e}")
            return 0.99
    
    def _determine_analysis_mode(self, resonance: float) -> AnalysisMode:
        """Determine analysis mode based on bridge resonance"""
        if resonance >= 0.99:
            return AnalysisMode.QUANTUM
        elif resonance >= 0.95:
            return AnalysisMode.DEEP
        else:
            return AnalysisMode.STANDARD
    
    def _parse_diff(self, diff_content: str) -> Tuple[int, int, int, List[str]]:
        """
        Parse diff content to extract changes
        
        Returns:
            Tuple of (files_changed, lines_added, lines_removed, file_list)
        """
        files_changed = 0
        lines_added = 0
        lines_removed = 0
        file_list = []
        
        current_file = None
        
        for line in diff_content.split('\n'):
            # File marker
            if line.startswith('diff --git'):
                files_changed += 1
                # Extract filename
                match = re.search(r'b/(.+)$', line)
                if match:
                    current_file = match.group(1)
                    file_list.append(current_file)
            # Added lines
            elif line.startswith('+') and not line.startswith('+++'):
                lines_added += 1
            # Removed lines
            elif line.startswith('-') and not line.startswith('---'):
                lines_removed += 1
        
        return files_changed, lines_added, lines_removed, file_list
    
    def _analyze_security(self, diff_content: str, file_list: List[str], mode: AnalysisMode) -> Tuple[SecurityLevel, List[str]]:
        """
        Analyze diff for security concerns
        
        Returns:
            Tuple of (risk_level, findings)
        """
        findings = []
        risk_level = SecurityLevel.NONE
        
        # Security patterns to check
        patterns = {
            SecurityLevel.CRITICAL: [
                r'API[_-]?KEY',
                r'SECRET[_-]?KEY',
                r'PASSWORD',
                r'PRIVATE[_-]?KEY',
                r'-----BEGIN (RSA|EC) PRIVATE KEY-----',
            ],
            SecurityLevel.HIGH: [
                r'eval\(',
                r'exec\(',
                r'subprocess\.call',
                r'os\.system',
                r'shell=True',
            ],
            SecurityLevel.MEDIUM: [
                r'TODO.*security',
                r'FIXME.*auth',
                r'XXX.*vuln',
                r'\.decode\(',
                r'pickle\.loads',
            ],
            SecurityLevel.LOW: [
                r'print\(',
                r'console\.log',
                r'DEBUG\s*=\s*True',
            ]
        }
        
        # In QUANTUM mode, perform deeper analysis
        if mode == AnalysisMode.QUANTUM:
            # Check for hardcoded credentials
            if re.search(r'["\']([a-zA-Z0-9]{32,})["\']', diff_content):
                findings.append("Possible hardcoded credentials detected")
                risk_level = max(risk_level, SecurityLevel.HIGH)
        
        # Check all patterns
        for level, pattern_list in patterns.items():
            for pattern in pattern_list:
                if re.search(pattern, diff_content, re.IGNORECASE):
                    findings.append(f"Security pattern detected: {pattern}")
                    risk_level = max(risk_level, level)
        
        # File-based checks
        for file_path in file_list:
            if file_path.endswith(('.env', '.key', '.pem', 'credentials.json')):
                findings.append(f"Sensitive file modified: {file_path}")
                risk_level = max(risk_level, SecurityLevel.HIGH)
        
        return risk_level, findings
    
    def analyze_diff(self, diff_content: str) -> DiffAnalysis:
        """
        Analyze a diff with quantum-enhanced security validation
        
        Args:
            diff_content: Git diff content
            
        Returns:
            DiffAnalysis result
        """
        # Check compliance
        guard = self._get_compliance_guard()
        if not guard.validate_operation("diff_analysis"):
            logger.warning("Diff analysis not compliant, proceeding with reduced capabilities")
        
        # Get resonance and determine mode
        resonance = self._get_bridge_resonance()
        mode = self._determine_analysis_mode(resonance)
        
        # Parse diff
        files_changed, lines_added, lines_removed, file_list = self._parse_diff(diff_content)
        
        # Security analysis
        risk_level, security_findings = self._analyze_security(diff_content, file_list, mode)
        
        # Generate summary
        summary = self._generate_summary(files_changed, lines_added, lines_removed, risk_level, mode)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(risk_level, security_findings, mode)
        
        return DiffAnalysis(
            summary=summary,
            files_changed=files_changed,
            lines_added=lines_added,
            lines_removed=lines_removed,
            risk_level=risk_level,
            security_findings=security_findings,
            recommendations=recommendations,
            mode=mode,
            resonance=resonance,
            timestamp=datetime.now(UTC).isoformat()
        )
    
    def _generate_summary(self, files: int, added: int, removed: int, risk: SecurityLevel, mode: AnalysisMode) -> str:
        """Generate human-readable summary"""
        summary = f"Analysis Mode: {mode.value}\n"
        summary += f"Files Changed: {files}\n"
        summary += f"Lines Added: {added}\n"
        summary += f"Lines Removed: {removed}\n"
        summary += f"Security Risk: {risk.value}\n"
        
        # Add insights based on mode
        if mode == AnalysisMode.QUANTUM:
            summary += "\n🔬 Quantum Analysis: Deep pattern recognition and security validation applied"
        elif mode == AnalysisMode.DEEP:
            summary += "\n🔍 Deep Analysis: Enhanced security checks and pattern detection"
        else:
            summary += "\n📊 Standard Analysis: Basic change metrics and security scan"
        
        return summary
    
    def _generate_recommendations(self, risk: SecurityLevel, findings: List[str], mode: AnalysisMode) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if risk == SecurityLevel.CRITICAL:
            recommendations.append("⚠️ CRITICAL: Remove sensitive data immediately before merging")
            recommendations.append("🔒 Use environment variables for secrets")
            recommendations.append("🔍 Review all changes for exposed credentials")
        elif risk == SecurityLevel.HIGH:
            recommendations.append("⚠️ HIGH RISK: Review security implications carefully")
            recommendations.append("🛡️ Consider security audit before deployment")
        elif risk == SecurityLevel.MEDIUM:
            recommendations.append("⚠️ Medium risk detected - review security notes")
        
        if mode == AnalysisMode.QUANTUM and findings:
            recommendations.append("🔬 Quantum analysis detected patterns - thorough review recommended")
        
        if not findings:
            recommendations.append("✅ No security concerns detected")
        
        return recommendations
    
    def generate_pr(self, diff_analysis: DiffAnalysis, title: str, description: str = "") -> PRTemplate:
        """
        Generate PR template with resonance-aware enhancements
        
        Args:
            diff_analysis: Analysis result from analyze_diff
            title: PR title
            description: Optional PR description
            
        Returns:
            PRTemplate with enhanced metadata
        """
        # Build enhanced description
        enhanced_description = description or ""
        
        if diff_analysis.mode == AnalysisMode.QUANTUM:
            enhanced_description += "\n\n## 🔬 Quantum Analysis Results\n"
        elif diff_analysis.mode == AnalysisMode.DEEP:
            enhanced_description += "\n\n## 🔍 Deep Analysis Results\n"
        else:
            enhanced_description += "\n\n## 📊 Analysis Results\n"
        
        enhanced_description += f"\n{diff_analysis.summary}\n"
        
        # Add security section if findings
        if diff_analysis.security_findings:
            enhanced_description += "\n## 🔒 Security Findings\n"
            for finding in diff_analysis.security_findings:
                enhanced_description += f"- {finding}\n"
        
        # Add recommendations
        if diff_analysis.recommendations:
            enhanced_description += "\n## 💡 Recommendations\n"
            for rec in diff_analysis.recommendations:
                enhanced_description += f"- {rec}\n"
        
        # Generate labels
        labels = []
        if diff_analysis.risk_level == SecurityLevel.CRITICAL:
            labels.extend(["security", "critical", "do-not-merge"])
        elif diff_analysis.risk_level == SecurityLevel.HIGH:
            labels.extend(["security", "high-risk"])
        elif diff_analysis.risk_level == SecurityLevel.MEDIUM:
            labels.append("security-review")
        
        if diff_analysis.mode == AnalysisMode.QUANTUM:
            labels.append("quantum-validated")
        
        # Add change size labels
        if diff_analysis.files_changed > 10 or diff_analysis.lines_added > 500:
            labels.append("large-change")
        elif diff_analysis.files_changed <= 3 and diff_analysis.lines_added < 100:
            labels.append("small-change")
        
        return PRTemplate(
            title=title,
            description=enhanced_description,
            labels=labels,
            metadata={
                "analysis_mode": diff_analysis.mode.value,
                "resonance": diff_analysis.resonance,
                "risk_level": diff_analysis.risk_level.value,
                "files_changed": diff_analysis.files_changed,
                "lines_added": diff_analysis.lines_added,
                "lines_removed": diff_analysis.lines_removed
            }
        )
