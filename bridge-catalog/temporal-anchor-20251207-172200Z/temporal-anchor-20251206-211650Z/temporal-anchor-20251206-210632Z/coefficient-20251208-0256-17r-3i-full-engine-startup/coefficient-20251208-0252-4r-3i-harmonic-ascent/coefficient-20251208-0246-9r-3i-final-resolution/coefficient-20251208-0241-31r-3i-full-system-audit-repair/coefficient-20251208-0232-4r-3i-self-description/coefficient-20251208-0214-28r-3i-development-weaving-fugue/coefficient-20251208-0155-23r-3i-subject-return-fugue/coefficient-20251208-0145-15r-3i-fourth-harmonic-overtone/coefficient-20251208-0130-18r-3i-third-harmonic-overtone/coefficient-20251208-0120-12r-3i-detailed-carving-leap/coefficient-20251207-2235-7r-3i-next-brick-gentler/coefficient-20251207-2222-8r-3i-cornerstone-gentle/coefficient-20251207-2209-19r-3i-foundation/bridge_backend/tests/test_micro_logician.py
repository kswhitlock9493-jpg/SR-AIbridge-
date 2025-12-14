"""
Test Sovereign MicroLogician Engine
"""

import pytest
from bridge_backend.bridge_engines.micro_logician import (
    SovereignMicroLogician,
    LogAnalysis,
    ThreatLevel,
    AnomalyType,
    SecurityFinding,
    PerformanceMetrics,
    Anomaly
)


class TestSovereignMicroLogician:
    """Test the Sovereign MicroLogician Engine"""
    
    def test_micrologician_initialization(self):
        """Test MicroLogician initializes correctly"""
        engine = SovereignMicroLogician()
        assert engine.min_resonance == 0.90
        assert engine._compliance_guard is None  # Lazy loaded
        assert len(engine.security_patterns) > 0
        assert len(engine.performance_patterns) > 0
    
    def test_determine_analysis_mode(self):
        """Test analysis mode determination"""
        engine = SovereignMicroLogician()
        
        assert engine._determine_analysis_mode(0.99) == "QUANTUM"
        assert engine._determine_analysis_mode(0.97) == "DEEP"
        assert engine._determine_analysis_mode(0.90) == "STANDARD"
    
    def test_parse_log_levels(self):
        """Test log level parsing"""
        engine = SovereignMicroLogician()
        
        log_content = """
2025-11-05 12:00:00 INFO Application started
2025-11-05 12:01:00 ERROR Database connection failed
2025-11-05 12:02:00 WARNING Cache miss
2025-11-05 12:03:00 DEBUG Processing request
2025-11-05 12:04:00 ERROR Authentication failed
"""
        
        levels = engine._parse_log_levels(log_content)
        
        assert "ERROR" in levels
        assert levels["ERROR"] >= 2
        assert "WARNING" in levels
        assert levels["WARNING"] >= 1
        assert "INFO" in levels
        assert "DEBUG" in levels
    
    def test_analyze_logs_simple(self):
        """Test simple log analysis"""
        engine = SovereignMicroLogician()
        
        log_content = """
2025-11-05 12:00:00 INFO Application started
2025-11-05 12:01:00 INFO Processing request
2025-11-05 12:02:00 INFO Request completed
"""
        
        analysis = engine.analyze_logs(log_content)
        
        assert isinstance(analysis, LogAnalysis)
        assert analysis.total_lines >= 3
        assert isinstance(analysis.log_levels, dict)
        assert isinstance(analysis.security_findings, list)
        assert isinstance(analysis.performance_metrics, PerformanceMetrics)
        assert isinstance(analysis.anomalies, list)
        assert isinstance(analysis.patterns, dict)
        assert isinstance(analysis.recommendations, list)
        assert 0.0 <= analysis.confidence <= 1.0
        assert analysis.mode in ["STANDARD", "DEEP", "QUANTUM"]
    
    def test_security_analysis_critical_threat(self):
        """Test security analysis detects critical threats"""
        engine = SovereignMicroLogician()
        
        log_content = """
2025-11-05 12:00:00 ERROR Login failed for user admin
2025-11-05 12:01:00 INFO password: mysecretpassword123
2025-11-05 12:02:00 ERROR API_KEY leaked: sk_live_1234567890
"""
        
        analysis = engine.analyze_logs(log_content)
        
        # Should detect credential exposure
        assert len(analysis.security_findings) > 0
        critical_findings = [f for f in analysis.security_findings if f.threat_level == ThreatLevel.CRITICAL]
        assert len(critical_findings) > 0
    
    def test_security_analysis_safe_logs(self):
        """Test security analysis on safe logs"""
        engine = SovereignMicroLogician()
        
        log_content = """
2025-11-05 12:00:00 INFO Application started
2025-11-05 12:01:00 INFO Request processed successfully
2025-11-05 12:02:00 INFO User logged in
"""
        
        analysis = engine.analyze_logs(log_content)
        
        # Should have minimal or no security findings
        critical_findings = [f for f in analysis.security_findings if f.threat_level == ThreatLevel.CRITICAL]
        assert len(critical_findings) == 0
    
    def test_performance_analysis(self):
        """Test performance metrics analysis"""
        engine = SovereignMicroLogician()
        
        log_content = """
2025-11-05 12:00:00 INFO Request started
2025-11-05 12:01:00 ERROR Database query failed
2025-11-05 12:02:00 WARNING Slow query detected: 5000ms
2025-11-05 12:03:00 ERROR Connection timeout
2025-11-05 12:04:00 INFO Request completed
"""
        
        analysis = engine.analyze_logs(log_content)
        metrics = analysis.performance_metrics
        
        assert isinstance(metrics, PerformanceMetrics)
        assert metrics.total_events > 0
        assert 0.0 <= metrics.error_rate <= 1.0
        assert 0.0 <= metrics.warning_rate <= 1.0
        assert isinstance(metrics.bottlenecks, list)
    
    def test_anomaly_detection_error_spike(self):
        """Test anomaly detection for error spikes"""
        engine = SovereignMicroLogician()
        
        # Generate log with many errors
        error_lines = "\n".join([f"2025-11-05 12:{i:02d}:00 ERROR Something went wrong" for i in range(20)])
        log_content = f"""
{error_lines}
2025-11-05 13:00:00 INFO Application running
"""
        
        analysis = engine.analyze_logs(log_content)
        
        # Should detect error spike
        error_anomalies = [a for a in analysis.anomalies if a.type == AnomalyType.ERROR_SPIKE]
        assert len(error_anomalies) > 0
    
    def test_pattern_extraction(self):
        """Test pattern extraction from logs"""
        engine = SovereignMicroLogician()
        
        log_content = """
2025-11-05 12:00:00 INFO GET /api/users
2025-11-05 12:01:00 INFO POST /api/users
2025-11-05 12:02:00 INFO SELECT * FROM users
2025-11-05 12:03:00 ERROR Exception: ValueError
2025-11-05 12:04:00 INFO User login successful
"""
        
        analysis = engine.analyze_logs(log_content)
        patterns = analysis.patterns
        
        assert isinstance(patterns, dict)
        # Should detect HTTP requests and database queries
        assert any("HTTP" in key or "Database" in key for key in patterns.keys())
    
    def test_generate_summary(self):
        """Test summary generation"""
        engine = SovereignMicroLogician()
        
        log_levels = {"ERROR": 5, "INFO": 10, "WARNING": 2}
        metrics = PerformanceMetrics(
            total_events=17,
            error_rate=0.29,
            warning_rate=0.12,
            bottlenecks=["Slow Query"],
            avg_event_length=100.0
        )
        
        summary = engine._generate_summary(
            total=17,
            levels=log_levels,
            findings=2,
            metrics=metrics,
            anomalies=1,
            mode="QUANTUM"
        )
        
        assert "QUANTUM" in summary
        assert "17" in summary
        assert "ERROR=5" in summary
    
    def test_generate_recommendations_critical(self):
        """Test recommendations for critical findings"""
        engine = SovereignMicroLogician()
        
        findings = [
            SecurityFinding(
                threat_level=ThreatLevel.CRITICAL,
                category="Credential exposure",
                description="Password detected",
                recommendation="Rotate credentials"
            )
        ]
        
        metrics = PerformanceMetrics(
            total_events=10,
            error_rate=0.5,
            warning_rate=0.2,
            bottlenecks=[],
            avg_event_length=100.0
        )
        
        recommendations = engine._generate_recommendations(
            findings=findings,
            metrics=metrics,
            anomalies=[],
            mode="QUANTUM"
        )
        
        assert len(recommendations) > 0
        assert any("CRITICAL" in rec for rec in recommendations)
    
    def test_confidence_calculation(self):
        """Test confidence score calculation"""
        engine = SovereignMicroLogician()
        
        # High resonance, good data
        confidence = engine._calculate_confidence(0.99, 1000, "QUANTUM")
        assert 0.9 <= confidence <= 1.0
        
        # Low data points
        confidence = engine._calculate_confidence(0.99, 5, "QUANTUM")
        assert confidence < 0.6
        
        # Standard mode
        confidence = engine._calculate_confidence(0.90, 1000, "STANDARD")
        assert confidence <= 0.9
    
    def test_get_security_recommendation(self):
        """Test security recommendation generation"""
        engine = SovereignMicroLogician()
        
        rec_critical = engine._get_security_recommendation(ThreatLevel.CRITICAL, "test")
        assert "IMMEDIATE" in rec_critical or "CRITICAL" in rec_critical
        
        rec_low = engine._get_security_recommendation(ThreatLevel.LOW, "test")
        assert "Monitor" in rec_low or "consider" in rec_low
