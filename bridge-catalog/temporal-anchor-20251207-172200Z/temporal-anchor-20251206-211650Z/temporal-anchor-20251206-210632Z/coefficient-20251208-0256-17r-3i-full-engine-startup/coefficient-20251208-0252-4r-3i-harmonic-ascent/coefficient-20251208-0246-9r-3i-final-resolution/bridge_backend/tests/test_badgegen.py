"""
Tests for Badge Generator
"""

import pytest
import tempfile
import json
from pathlib import Path
from bridge_backend.cli.badgegen import (
    load_health_record,
    determine_badge_color,
    generate_svg_badge,
    get_color_hex,
    generate_markdown_badge
)


class TestLoadHealthRecord:
    """Test health record loading"""
    
    def test_load_valid_record(self):
        """Test loading valid health record"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            record = {
                "bridge_health_score": 100,
                "status": "passing",
                "truth_certified": True,
                "auto_heals": 0,
                "timestamp": "2025-10-13T00:00:00Z"
            }
            json.dump(record, f)
            temp_path = f.name
        
        try:
            result = load_health_record(temp_path)
            assert result["bridge_health_score"] == 100
        finally:
            import os
            os.unlink(temp_path)
    
    def test_load_missing_record(self):
        """Test loading non-existent record exits"""
        with pytest.raises(SystemExit):
            load_health_record("/nonexistent/record.json")


class TestDetermineBadgeColor:
    """Test badge color determination"""
    
    def test_color_green(self):
        """Test green color for >= 95%"""
        assert determine_badge_color(100) == "brightgreen"
        assert determine_badge_color(95) == "brightgreen"
    
    def test_color_yellow(self):
        """Test yellow color for 80-94%"""
        assert determine_badge_color(94) == "yellow"
        assert determine_badge_color(80) == "yellow"
    
    def test_color_red(self):
        """Test red color for < 80%"""
        assert determine_badge_color(79) == "red"
        assert determine_badge_color(50) == "red"
        assert determine_badge_color(0) == "red"


class TestGetColorHex:
    """Test color hex conversion"""
    
    def test_known_colors(self):
        """Test conversion of known colors"""
        assert get_color_hex("brightgreen") == "4c1"
        assert get_color_hex("yellow") == "dfb317"
        assert get_color_hex("red") == "e05d44"
        assert get_color_hex("blue") == "007ec6"
    
    def test_unknown_color(self):
        """Test unknown color defaults to grey"""
        assert get_color_hex("unknown") == "9f9f9f"


class TestGenerateSvgBadge:
    """Test SVG badge generation"""
    
    def test_generate_passing_badge(self):
        """Test SVG for passing status"""
        record = {
            "bridge_health_score": 100,
            "truth_certified": True,
            "status": "passing",
            "auto_heals": 0,
            "timestamp": "2025-10-13T00:00:00Z"
        }
        
        svg = generate_svg_badge(record)
        
        assert "<svg" in svg
        assert "Bridge Health" in svg
        assert "100%" in svg
        assert "Truth Certified" in svg
        assert "#4c1" in svg  # Green color
    
    def test_generate_warning_badge(self):
        """Test SVG for warning status"""
        record = {
            "bridge_health_score": 85,
            "truth_certified": True,
            "status": "warning",
            "auto_heals": 2,
            "timestamp": "2025-10-13T00:00:00Z"
        }
        
        svg = generate_svg_badge(record)
        
        assert "85%" in svg
        assert "Truth Certified" in svg
        assert "#dfb317" in svg  # Yellow color
    
    def test_generate_critical_badge(self):
        """Test SVG for critical status"""
        record = {
            "bridge_health_score": 50,
            "truth_certified": False,
            "status": "critical",
            "auto_heals": 5,
            "timestamp": "2025-10-13T00:00:00Z"
        }
        
        svg = generate_svg_badge(record)
        
        assert "50%" in svg
        assert "Not Certified" in svg
        assert "#e05d44" in svg  # Red color
    
    def test_svg_valid_xml(self):
        """Test that generated SVG is valid XML"""
        record = {
            "bridge_health_score": 100,
            "truth_certified": True,
            "status": "passing",
            "auto_heals": 0,
            "timestamp": "2025-10-13T00:00:00Z"
        }
        
        svg = generate_svg_badge(record)
        
        # Basic XML validation
        assert svg.startswith("<svg")
        assert svg.endswith("</svg>")
        assert 'xmlns="http://www.w3.org/2000/svg"' in svg


class TestGenerateMarkdownBadge:
    """Test Markdown badge generation"""
    
    def test_generate_passing_markdown(self):
        """Test Markdown for passing status"""
        record = {
            "bridge_health_score": 100,
            "truth_certified": True,
            "status": "passing",
            "auto_heals": 0,
            "timestamp": "2025-10-13T00:00:00Z"
        }
        
        md = generate_markdown_badge(record, "docs/badges/bridge_health.svg")
        
        assert "🟢" in md
        assert "100%" in md
        assert "PASSING" in md
        assert "✅ Yes" in md
        assert "![Bridge Health](docs/badges/bridge_health.svg)" in md
        assert "## Integration" in md
    
    def test_generate_warning_markdown(self):
        """Test Markdown for warning status"""
        record = {
            "bridge_health_score": 85,
            "truth_certified": True,
            "status": "warning",
            "auto_heals": 2,
            "timestamp": "2025-10-13T00:00:00Z"
        }
        
        md = generate_markdown_badge(record, "docs/badges/bridge_health.svg")
        
        assert "🟡" in md
        assert "85%" in md
        assert "WARNING" in md
        assert "Auto-Heals:** 2" in md
    
    def test_generate_critical_markdown(self):
        """Test Markdown for critical status"""
        record = {
            "bridge_health_score": 50,
            "truth_certified": False,
            "status": "critical",
            "auto_heals": 5,
            "timestamp": "2025-10-13T00:00:00Z"
        }
        
        md = generate_markdown_badge(record, "docs/badges/bridge_health.svg")
        
        assert "🔴" in md
        assert "50%" in md
        assert "CRITICAL" in md
        assert "❌ No" in md
        assert "Auto-Heals:** 5" in md


class TestBadgeIntegration:
    """Integration tests for badge generation"""
    
    def test_full_badge_generation_workflow(self):
        """Test complete badge generation workflow"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create health record
            record_path = Path(tmpdir) / "health.json"
            record = {
                "bridge_health_score": 95,
                "truth_certified": True,
                "status": "passing",
                "auto_heals": 1,
                "timestamp": "2025-10-13T00:00:00Z",
                "selftest": {"total_tests": 10, "passed_tests": 10},
                "umbra": {"critical_count": 0, "warning_count": 0}
            }
            with open(record_path, 'w') as f:
                json.dump(record, f)
            
            # Load record
            loaded = load_health_record(str(record_path))
            assert loaded["bridge_health_score"] == 95
            
            # Generate SVG
            svg = generate_svg_badge(loaded)
            assert "95%" in svg
            assert "#4c1" in svg  # Green
            
            # Generate Markdown
            md = generate_markdown_badge(loaded, "test.svg")
            assert "95%" in md
            assert "🟢" in md
    
    def test_boundary_scores(self):
        """Test badge generation at boundary scores"""
        # Test 95% (green)
        record_95 = {
            "bridge_health_score": 95,
            "truth_certified": True,
            "status": "passing",
            "auto_heals": 0,
            "timestamp": "2025-10-13T00:00:00Z"
        }
        assert determine_badge_color(95) == "brightgreen"
        svg_95 = generate_svg_badge(record_95)
        assert "#4c1" in svg_95
        
        # Test 94% (yellow)
        record_94 = {
            "bridge_health_score": 94,
            "truth_certified": True,
            "status": "warning",
            "auto_heals": 0,
            "timestamp": "2025-10-13T00:00:00Z"
        }
        assert determine_badge_color(94) == "yellow"
        svg_94 = generate_svg_badge(record_94)
        assert "#dfb317" in svg_94
        
        # Test 80% (yellow)
        record_80 = {
            "bridge_health_score": 80,
            "truth_certified": True,
            "status": "warning",
            "auto_heals": 0,
            "timestamp": "2025-10-13T00:00:00Z"
        }
        assert determine_badge_color(80) == "yellow"
        
        # Test 79% (red)
        record_79 = {
            "bridge_health_score": 79,
            "truth_certified": True,
            "status": "critical",
            "auto_heals": 0,
            "timestamp": "2025-10-13T00:00:00Z"
        }
        assert determine_badge_color(79) == "red"
        svg_79 = generate_svg_badge(record_79)
        assert "#e05d44" in svg_79
