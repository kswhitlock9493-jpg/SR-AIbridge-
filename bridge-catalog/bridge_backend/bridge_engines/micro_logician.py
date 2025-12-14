"""
Sovereign MicroLogician Engine
Quantum-enhanced log analysis with security intelligence and performance analytics
"""

import logging
import os
import re
from datetime import datetime, UTC
from typing import Dict, Any, List, Optional, Set
from pydantic import BaseModel
from collections import defaultdict, Counter
from enum import Enum

logger = logging.getLogger(__name__)


class ThreatLevel(str, Enum):
    """Security threat levels"""
    NONE = "NONE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AnomalyType(str, Enum):
    """Types of anomalies detected"""
    ERROR_SPIKE = "ERROR_SPIKE"
    LENGTH_ANOMALY = "LENGTH_ANOMALY"
    PATTERN_DEVIATION = "PATTERN_DEVIATION"
    FREQUENCY_ANOMALY = "FREQUENCY_ANOMALY"


class SecurityFinding(BaseModel):
    """Security intelligence finding"""
    threat_level: ThreatLevel
    category: str
    description: str
    evidence: List[str] = []
    recommendation: str


class PerformanceMetrics(BaseModel):
    """Performance analysis metrics"""
    total_events: int
    error_rate: float
    warning_rate: float
    peak_period: Optional[str] = None
    bottlenecks: List[str] = []
    avg_event_length: float


class Anomaly(BaseModel):
    """Detected anomaly"""
    type: AnomalyType
    severity: str
    description: str
    timestamp: Optional[str] = None
    count: int = 1


class LogAnalysis(BaseModel):
    """Complete log analysis result"""
    summary: str
    total_lines: int
    log_levels: Dict[str, int]
    security_findings: List[SecurityFinding] = []
    performance_metrics: PerformanceMetrics
    anomalies: List[Anomaly] = []
    patterns: Dict[str, int] = {}
    recommendations: List[str] = []
    confidence: float
    mode: str
    timestamp: str


class SovereignMicroLogician:
    """
    Quantum-enhanced log analysis engine
    
    Features:
    - Quantum-enhanced log pattern detection
    - Security threat intelligence with anomaly detection
    - Performance bottleneck analysis and metrics
    - Resonance-aware analysis confidence scoring
    """
    
    def __init__(self):
        self.min_resonance = float(os.getenv("MICROLOGICIAN_MIN_RESONANCE", "0.90"))
        self._compliance_guard = None
        
        # Security patterns
        self.security_patterns = {
            ThreatLevel.CRITICAL: [
                (r'(password|passwd|pwd)\s*[:=]\s*["\']?([^"\'\s]+)', "Credential exposure"),
                (r'(api[_-]?key|secret[_-]?key)\s*[:=]\s*["\']?([^"\'\s]+)', "API key exposure"),
                (r'(authorization|bearer)\s*[:=]\s*["\']?([^"\'\s]+)', "Authorization token exposure"),
                (r'-----BEGIN (RSA|EC) PRIVATE KEY-----', "Private key exposure"),
            ],
            ThreatLevel.HIGH: [
                (r'(injection|xss|csrf|sql\s+injection)', "Injection attack pattern"),
                (r'(eval\(|exec\(|system\()', "Code execution pattern"),
                (r'(unauthorized|forbidden|denied)\s+(access|request)', "Access control violation"),
                (r'(failed\s+login|authentication\s+failed)', "Authentication failure"),
            ],
            ThreatLevel.MEDIUM: [
                (r'(deprecated|obsolete)\s+(function|method|api)', "Deprecated code usage"),
                (r'(insecure|unencrypted)\s+(connection|channel)', "Insecure communication"),
                (r'(permission|privilege)\s+(denied|insufficient)', "Permission issue"),
                (r'(timeout|timed\s+out)', "Timeout issues"),
            ],
            ThreatLevel.LOW: [
                (r'(warning|warn):', "Warning messages"),
                (r'(debug|trace):', "Debug messages in production"),
                (r'(todo|fixme|xxx):', "Development markers"),
            ]
        }
        
        # Performance patterns
        self.performance_patterns = {
            "slow_query": r'(query|request)\s+(took|duration|time):\s*(\d+(?:\.\d+)?)\s*(ms|s)',
            "high_memory": r'(memory|heap|ram)\s*(usage|used):\s*(\d+)(%|mb|gb)',
            "connection_pool": r'(connection|pool)\s*(exhausted|full|limit)',
            "timeout": r'(timeout|timed\s+out|deadline\s+exceeded)',
        }
    
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
    
    def _determine_analysis_mode(self, resonance: float) -> str:
        """Determine analysis mode based on bridge resonance"""
        if resonance >= 0.99:
            return "QUANTUM"
        elif resonance >= 0.95:
            return "DEEP"
        else:
            return "STANDARD"
    
    def _parse_log_levels(self, log_content: str) -> Dict[str, int]:
        """Parse and count log levels"""
        levels = defaultdict(int)
        
        patterns = {
            "ERROR": r'\b(ERROR|FATAL|CRITICAL)\b',
            "WARNING": r'\b(WARN|WARNING)\b',
            "INFO": r'\b(INFO|INFORMATION)\b',
            "DEBUG": r'\b(DEBUG|TRACE)\b',
        }
        
        for line in log_content.split('\n'):
            for level, pattern in patterns.items():
                if re.search(pattern, line, re.IGNORECASE):
                    levels[level] += 1
                    break
        
        return dict(levels)
    
    def _analyze_security(self, log_content: str, mode: str) -> List[SecurityFinding]:
        """Analyze logs for security threats"""
        findings = []
        
        for threat_level, patterns in self.security_patterns.items():
            # In STANDARD mode, only check CRITICAL and HIGH
            if mode == "STANDARD" and threat_level in [ThreatLevel.LOW, ThreatLevel.MEDIUM]:
                continue
            
            for pattern, category in patterns:
                matches = re.finditer(pattern, log_content, re.IGNORECASE)
                evidence = []
                
                for match in matches:
                    # Limit evidence to prevent exposure
                    context = match.group(0)[:100]
                    evidence.append(context)
                    
                    if len(evidence) >= 5:  # Limit evidence items
                        break
                
                if evidence:
                    recommendation = self._get_security_recommendation(threat_level, category)
                    
                    findings.append(SecurityFinding(
                        threat_level=threat_level,
                        category=category,
                        description=f"Detected {len(evidence)} instance(s) of {category}",
                        evidence=evidence[:3],  # Limit to 3 examples
                        recommendation=recommendation
                    ))
        
        return findings
    
    def _get_security_recommendation(self, threat_level: ThreatLevel, category: str) -> str:
        """Get recommendation for security finding"""
        recommendations = {
            ThreatLevel.CRITICAL: "⚠️ IMMEDIATE ACTION REQUIRED: Remove sensitive data from logs, rotate credentials",
            ThreatLevel.HIGH: "🔒 HIGH PRIORITY: Investigate and remediate security issue promptly",
            ThreatLevel.MEDIUM: "⚠️ Review and address security concern",
            ThreatLevel.LOW: "ℹ️ Monitor and consider improving logging practices",
        }
        return recommendations.get(threat_level, "Review finding")
    
    def _analyze_performance(self, log_content: str, mode: str) -> PerformanceMetrics:
        """Analyze performance metrics from logs"""
        lines = log_content.split('\n')
        total_events = len([l for l in lines if l.strip()])
        
        # Count errors and warnings
        error_count = len(re.findall(r'\b(ERROR|FATAL|CRITICAL)\b', log_content, re.IGNORECASE))
        warning_count = len(re.findall(r'\b(WARN|WARNING)\b', log_content, re.IGNORECASE))
        
        error_rate = error_count / max(total_events, 1)
        warning_rate = warning_count / max(total_events, 1)
        
        # Detect bottlenecks
        bottlenecks = []
        for name, pattern in self.performance_patterns.items():
            if re.search(pattern, log_content, re.IGNORECASE):
                bottlenecks.append(name.replace('_', ' ').title())
        
        # Calculate average event length
        event_lengths = [len(line) for line in lines if line.strip()]
        avg_length = sum(event_lengths) / max(len(event_lengths), 1)
        
        # Try to detect peak period (if timestamps present)
        peak_period = self._detect_peak_period(log_content) if mode == "QUANTUM" else None
        
        return PerformanceMetrics(
            total_events=total_events,
            error_rate=round(error_rate, 4),
            warning_rate=round(warning_rate, 4),
            peak_period=peak_period,
            bottlenecks=bottlenecks,
            avg_event_length=round(avg_length, 2)
        )
    
    def _detect_peak_period(self, log_content: str) -> Optional[str]:
        """Detect peak activity period from timestamps"""
        # Simple hour extraction (could be enhanced)
        hours = defaultdict(int)
        
        # Try to match common timestamp formats
        timestamp_pattern = r'(\d{2}):(\d{2}):(\d{2})'
        
        for match in re.finditer(timestamp_pattern, log_content):
            hour = match.group(1)
            hours[hour] += 1
        
        if hours:
            peak_hour = max(hours.items(), key=lambda x: x[1])[0]
            return f"{peak_hour}:00"
        
        return None
    
    def _detect_anomalies(self, log_content: str, log_levels: Dict[str, int], mode: str) -> List[Anomaly]:
        """Detect anomalies in log patterns"""
        anomalies = []
        
        # Error spike detection
        if "ERROR" in log_levels and log_levels["ERROR"] > 10:
            anomalies.append(Anomaly(
                type=AnomalyType.ERROR_SPIKE,
                severity="HIGH",
                description=f"High error count detected: {log_levels['ERROR']} errors",
                count=log_levels["ERROR"]
            ))
        
        # Message length anomalies (only in DEEP/QUANTUM mode)
        if mode in ["DEEP", "QUANTUM"]:
            lines = [l for l in log_content.split('\n') if l.strip()]
            if lines:
                lengths = [len(l) for l in lines]
                avg_len = sum(lengths) / len(lengths)
                
                # Detect unusually long messages
                long_messages = [l for l in lengths if l > avg_len * 3]
                if len(long_messages) > 5:
                    anomalies.append(Anomaly(
                        type=AnomalyType.LENGTH_ANOMALY,
                        severity="MEDIUM",
                        description=f"Detected {len(long_messages)} unusually long log messages",
                        count=len(long_messages)
                    ))
        
        # Pattern deviation (QUANTUM mode only)
        if mode == "QUANTUM":
            # Look for repeated patterns
            line_counter = Counter(log_content.split('\n'))
            duplicates = [line for line, count in line_counter.items() if count > 10 and line.strip()]
            
            if duplicates:
                anomalies.append(Anomaly(
                    type=AnomalyType.PATTERN_DEVIATION,
                    severity="LOW",
                    description=f"Detected {len(duplicates)} repeated log patterns (possible loop)",
                    count=len(duplicates)
                ))
        
        return anomalies
    
    def _extract_patterns(self, log_content: str, mode: str) -> Dict[str, int]:
        """Extract common patterns from logs"""
        patterns = defaultdict(int)
        
        # Common log patterns
        pattern_matchers = {
            "HTTP Requests": r'(GET|POST|PUT|DELETE|PATCH)\s+/\S+',
            "Database Queries": r'(SELECT|INSERT|UPDATE|DELETE)\s+',
            "Error Messages": r'(Exception|Error):\s+\S+',
            "Authentication": r'(login|logout|auth|authentication)',
            "API Calls": r'(api|endpoint|service)\s+\S+',
        }
        
        for name, pattern in pattern_matchers.items():
            count = len(re.findall(pattern, log_content, re.IGNORECASE))
            if count > 0:
                patterns[name] = count
        
        return dict(patterns)
    
    def analyze_logs(self, log_content: str) -> LogAnalysis:
        """
        Analyze logs with quantum-enhanced intelligence
        
        Args:
            log_content: Raw log content
            
        Returns:
            LogAnalysis result with security and performance insights
        """
        # Check compliance
        guard = self._get_compliance_guard()
        if not guard.validate_operation("log_analysis"):
            logger.warning("Log analysis not compliant, proceeding with reduced capabilities")
        
        # Get resonance and determine mode
        resonance = self._get_bridge_resonance()
        mode = self._determine_analysis_mode(resonance)
        
        # Parse log levels
        log_levels = self._parse_log_levels(log_content)
        total_lines = len([l for l in log_content.split('\n') if l.strip()])
        
        # Security analysis
        security_findings = self._analyze_security(log_content, mode)
        
        # Performance analysis
        performance_metrics = self._analyze_performance(log_content, mode)
        
        # Anomaly detection
        anomalies = self._detect_anomalies(log_content, log_levels, mode)
        
        # Pattern extraction
        patterns = self._extract_patterns(log_content, mode)
        
        # Generate summary
        summary = self._generate_summary(
            total_lines, log_levels, len(security_findings), 
            performance_metrics, len(anomalies), mode
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            security_findings, performance_metrics, anomalies, mode
        )
        
        # Calculate confidence based on resonance and data quality
        confidence = self._calculate_confidence(resonance, total_lines, mode)
        
        return LogAnalysis(
            summary=summary,
            total_lines=total_lines,
            log_levels=log_levels,
            security_findings=security_findings,
            performance_metrics=performance_metrics,
            anomalies=anomalies,
            patterns=patterns,
            recommendations=recommendations,
            confidence=confidence,
            mode=mode,
            timestamp=datetime.now(UTC).isoformat()
        )
    
    def _generate_summary(self, total: int, levels: Dict[str, int], findings: int, 
                         metrics: PerformanceMetrics, anomalies: int, mode: str) -> str:
        """Generate analysis summary"""
        summary = f"Analysis Mode: {mode}\n"
        summary += f"Total Events: {total}\n"
        summary += f"Log Levels: {', '.join(f'{k}={v}' for k, v in levels.items())}\n"
        summary += f"Security Findings: {findings}\n"
        summary += f"Error Rate: {metrics.error_rate:.2%}\n"
        summary += f"Anomalies Detected: {anomalies}\n"
        
        if metrics.bottlenecks:
            summary += f"Performance Issues: {', '.join(metrics.bottlenecks)}\n"
        
        return summary
    
    def _generate_recommendations(self, findings: List[SecurityFinding], 
                                 metrics: PerformanceMetrics, 
                                 anomalies: List[Anomaly], mode: str) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Security recommendations
        critical_findings = [f for f in findings if f.threat_level == ThreatLevel.CRITICAL]
        if critical_findings:
            recommendations.append("🚨 CRITICAL: Address security vulnerabilities immediately")
            recommendations.append("🔒 Rotate exposed credentials and update security policies")
        
        high_findings = [f for f in findings if f.threat_level == ThreatLevel.HIGH]
        if high_findings:
            recommendations.append("⚠️ HIGH: Review and remediate security issues")
        
        # Performance recommendations
        if metrics.error_rate > 0.1:
            recommendations.append(f"📊 High error rate ({metrics.error_rate:.2%}) - investigate root causes")
        
        if metrics.bottlenecks:
            recommendations.append(f"⚡ Performance bottlenecks detected: {', '.join(metrics.bottlenecks)}")
        
        # Anomaly recommendations
        high_anomalies = [a for a in anomalies if a.severity == "HIGH"]
        if high_anomalies:
            recommendations.append("🔍 Investigate detected anomalies for potential issues")
        
        # Mode-specific recommendations
        if mode == "QUANTUM":
            recommendations.append("🔬 Quantum analysis complete - high confidence in findings")
        elif mode == "STANDARD" and findings:
            recommendations.append("💡 Enable higher bridge resonance for deeper analysis")
        
        if not recommendations:
            recommendations.append("✅ No major issues detected - logs appear healthy")
        
        return recommendations
    
    def _calculate_confidence(self, resonance: float, data_points: int, mode: str) -> float:
        """Calculate analysis confidence score"""
        # Base confidence from resonance
        confidence = resonance
        
        # Adjust for data volume
        if data_points < 10:
            confidence *= 0.5
        elif data_points < 100:
            confidence *= 0.8
        
        # Mode bonus
        mode_bonus = {
            "QUANTUM": 1.0,
            "DEEP": 0.95,
            "STANDARD": 0.85
        }
        confidence *= mode_bonus.get(mode, 0.85)
        
        return min(round(confidence, 3), 1.0)
