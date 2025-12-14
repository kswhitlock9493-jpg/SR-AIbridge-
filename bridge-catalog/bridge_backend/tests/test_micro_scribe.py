"""
Test Sovereign MicroScribe Engine
"""

import pytest
from bridge_backend.bridge_engines.micro_scribe import (
    SovereignMicroScribe,
    DiffAnalysis,
    PRTemplate,
    AnalysisMode,
    SecurityLevel
)


class TestSovereignMicroScribe:
    """Test the Sovereign MicroScribe Engine"""
    
    def test_microscribe_initialization(self):
        """Test MicroScribe initializes correctly"""
        engine = SovereignMicroScribe()
        assert engine.min_resonance == 0.90
        assert engine._compliance_guard is None  # Lazy loaded
    
    def test_determine_analysis_mode(self):
        """Test analysis mode determination based on resonance"""
        engine = SovereignMicroScribe()
        
        assert engine._determine_analysis_mode(0.99) == AnalysisMode.QUANTUM
        assert engine._determine_analysis_mode(0.97) == AnalysisMode.DEEP
        assert engine._determine_analysis_mode(0.90) == AnalysisMode.STANDARD
    
    def test_parse_diff_basic(self):
        """Test basic diff parsing"""
        engine = SovereignMicroScribe()
        
        diff = """diff --git a/test.py b/test.py
index 1234567..abcdefg 100644
--- a/test.py
+++ b/test.py
@@ -1,3 +1,4 @@
 def hello():
-    print("old")
+    print("new")
+    print("added")
"""
        
        files, added, removed, file_list = engine._parse_diff(diff)
        assert files == 1
        assert added >= 2
        assert removed >= 1
        assert "test.py" in file_list
    
    def test_analyze_diff_simple(self):
        """Test simple diff analysis"""
        engine = SovereignMicroScribe()
        
        diff = """diff --git a/README.md b/README.md
index 1234567..abcdefg 100644
--- a/README.md
+++ b/README.md
@@ -1,1 +1,2 @@
 # Test
+New line
"""
        
        analysis = engine.analyze_diff(diff)
        
        assert isinstance(analysis, DiffAnalysis)
        assert analysis.files_changed >= 1
        assert analysis.lines_added >= 1
        assert isinstance(analysis.risk_level, SecurityLevel)
        assert isinstance(analysis.mode, AnalysisMode)
        assert 0.0 <= analysis.resonance <= 1.0
        assert analysis.timestamp is not None
    
    def test_security_analysis_critical_pattern(self):
        """Test security analysis detects critical patterns"""
        engine = SovereignMicroScribe()
        
        diff = """diff --git a/config.py b/config.py
+API_KEY = "sk_live_1234567890abcdef"
+PASSWORD = "mysecret123"
"""
        
        analysis = engine.analyze_diff(diff)
        
        # Should detect sensitive data
        assert analysis.risk_level in [SecurityLevel.HIGH, SecurityLevel.CRITICAL]
        assert len(analysis.security_findings) > 0
    
    def test_security_analysis_safe_diff(self):
        """Test security analysis on safe diff"""
        engine = SovereignMicroScribe()
        
        diff = """diff --git a/utils.py b/utils.py
+def add(a, b):
+    return a + b
"""
        
        analysis = engine.analyze_diff(diff)
        
        # Should be low risk or none
        assert analysis.risk_level in [SecurityLevel.NONE, SecurityLevel.LOW]
    
    def test_generate_pr_basic(self):
        """Test PR template generation"""
        engine = SovereignMicroScribe()
        
        # Create a simple analysis
        diff = """diff --git a/test.py b/test.py
+# Simple change
"""
        analysis = engine.analyze_diff(diff)
        
        pr = engine.generate_pr(analysis, "Test PR", "Test description")
        
        assert isinstance(pr, PRTemplate)
        assert pr.title == "Test PR"
        assert "Test description" in pr.description
        assert isinstance(pr.labels, list)
        assert "analysis_mode" in pr.metadata
    
    def test_generate_pr_with_security_findings(self):
        """Test PR generation includes security findings"""
        engine = SovereignMicroScribe()
        
        diff = """diff --git a/config.py b/config.py
+SECRET_KEY = "dangerous_secret"
"""
        analysis = engine.analyze_diff(diff)
        pr = engine.generate_pr(analysis, "Security Test PR")
        
        # Should have security labels if critical/high risk
        if analysis.risk_level in [SecurityLevel.CRITICAL, SecurityLevel.HIGH]:
            assert any("security" in label.lower() for label in pr.labels)
    
    def test_generate_summary(self):
        """Test summary generation"""
        engine = SovereignMicroScribe()
        
        summary = engine._generate_summary(
            files=5,
            added=100,
            removed=50,
            risk=SecurityLevel.MEDIUM,
            mode=AnalysisMode.DEEP
        )
        
        assert "Files Changed: 5" in summary
        assert "Lines Added: 100" in summary
        assert "Lines Removed: 50" in summary
        assert "MEDIUM" in summary
    
    def test_generate_recommendations_critical(self):
        """Test recommendations for critical findings"""
        engine = SovereignMicroScribe()
        
        recommendations = engine._generate_recommendations(
            risk=SecurityLevel.CRITICAL,
            findings=["Credential exposure"],
            mode=AnalysisMode.QUANTUM
        )
        
        assert len(recommendations) > 0
        assert any("CRITICAL" in rec for rec in recommendations)
    
    def test_generate_recommendations_safe(self):
        """Test recommendations for safe changes"""
        engine = SovereignMicroScribe()
        
        recommendations = engine._generate_recommendations(
            risk=SecurityLevel.NONE,
            findings=[],
            mode=AnalysisMode.STANDARD
        )
        
        assert len(recommendations) > 0
        assert any("No security concerns" in rec for rec in recommendations)
