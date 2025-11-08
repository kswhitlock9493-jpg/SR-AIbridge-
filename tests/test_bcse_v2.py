#!/usr/bin/env python3
"""
Tests for BCSE v2 - Sovereign Autocorrect Engine
Tests the new BCSE++ modules including placeholders, refactor, prodcheck, and rewriters.
"""
import pytest
import sys
import os
import tempfile
import shutil
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestPlaceholders:
    """Test placeholder detection module"""

    def test_placeholders_import(self):
        """Test that placeholders module can be imported"""
        from bridge_tools.bcse import placeholders
        assert placeholders is not None

    def test_scan_detects_todo(self):
        """Test that scan detects TODO patterns"""
        from bridge_tools.bcse.placeholders import scan
        
        # Create a temporary directory with test files
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("# TODO: Fix this later\nprint('hello')")
            
            hits = scan(tmpdir)
            assert len(hits) > 0, "Should detect TODO pattern"
            assert any("TODO" in hit[2] for hit in hits), "Should find TODO in snippet"

    def test_scan_detects_fixme(self):
        """Test that scan detects FIXME patterns"""
        from bridge_tools.bcse.placeholders import scan
        
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("# FIXME: This is broken\npass")
            
            hits = scan(tmpdir)
            assert len(hits) > 0, "Should detect FIXME pattern"

    def test_scan_detects_localhost(self):
        """Test that scan detects localhost URLs"""
        from bridge_tools.bcse.placeholders import scan
        
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text('url = "http://localhost:8000"')
            
            hits = scan(tmpdir)
            assert len(hits) > 0, "Should detect localhost URL"

    def test_scan_skips_ignored_dirs(self):
        """Test that scan skips common ignored directories"""
        from bridge_tools.bcse.placeholders import scan
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a node_modules directory with TODO
            node_dir = Path(tmpdir) / "node_modules"
            node_dir.mkdir()
            (node_dir / "test.js").write_text("// TODO: ignored")
            
            # Create a regular file with TODO
            (Path(tmpdir) / "real.py").write_text("# TODO: should detect")
            
            hits = scan(tmpdir)
            # Should only detect the real.py TODO, not node_modules
            assert len(hits) == 1, "Should skip node_modules directory"


class TestRefactor:
    """Test code refactoring module"""

    def test_refactor_import(self):
        """Test that refactor module can be imported"""
        from bridge_tools.bcse import refactor
        assert refactor is not None

    def test_improve_on_directory(self):
        """Test improve function on a directory"""
        from bridge_tools.bcse.refactor import improve
        
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "test.py").write_text("x = 1\n")
            
            result = improve([tmpdir])
            assert result == 0, "Should return 0 on success"


class TestProdCheck:
    """Test production readiness check module"""

    def test_prodcheck_import(self):
        """Test that prodcheck module can be imported"""
        from bridge_tools.bcse import prodcheck
        assert prodcheck is not None

    def test_env_asserts_fails_with_debug_true(self):
        """Test that env assertions fail when DEBUG=true"""
        from bridge_tools.bcse.prodcheck import _env_asserts
        
        # Set DEBUG to true temporarily
        old_debug = os.environ.get("DEBUG")
        os.environ["DEBUG"] = "true"
        
        try:
            result = _env_asserts()
            # Should fail because DEBUG is true
            assert result == 1, "Should fail when DEBUG=true"
        finally:
            if old_debug:
                os.environ["DEBUG"] = old_debug
            else:
                os.environ.pop("DEBUG", None)

    def test_env_asserts_fails_with_cors_allow_all(self):
        """Test that env assertions fail when CORS_ALLOW_ALL=true"""
        from bridge_tools.bcse.prodcheck import _env_asserts
        
        old_cors = os.environ.get("CORS_ALLOW_ALL")
        os.environ["CORS_ALLOW_ALL"] = "true"
        
        try:
            result = _env_asserts()
            assert result == 1, "Should fail when CORS_ALLOW_ALL=true"
        finally:
            if old_cors:
                os.environ["CORS_ALLOW_ALL"] = old_cors
            else:
                os.environ.pop("CORS_ALLOW_ALL", None)

    def test_port_open_check(self):
        """Test port open detection"""
        from bridge_tools.bcse.prodcheck import _port_open
        
        # Test a port that should be closed
        result = _port_open("127.0.0.1", 9999, timeout=1)
        assert isinstance(result, bool)


class TestRewriters:
    """Test localhost to Forge rewriter module"""

    def test_rewriters_import(self):
        """Test that rewriters module can be imported"""
        from bridge_tools.bcse import rewriters
        assert rewriters is not None

    def test_rewrite_localhost_to_forge(self):
        """Test rewriting localhost URLs to Forge"""
        from bridge_tools.bcse.rewriters import rewrite_localhost_to_forge
        
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text('url = "http://localhost:8000/api"')
            
            # Set FORGE_DOMINION_ROOT for the test
            old_forge = os.environ.get("FORGE_DOMINION_ROOT")
            os.environ["FORGE_DOMINION_ROOT"] = "https://forge.example.com"
            
            try:
                # Test with dry_run=False to actually make changes
                changed = rewrite_localhost_to_forge([tmpdir], dry_run=False)
                
                # Check if file was changed
                new_content = test_file.read_text()
                assert "forge.example.com" in new_content, "Should replace localhost with Forge"
            finally:
                if old_forge:
                    os.environ["FORGE_DOMINION_ROOT"] = old_forge
                else:
                    os.environ.pop("FORGE_DOMINION_ROOT", None)

    def test_rewrite_without_forge_root(self):
        """Test rewrite behavior when FORGE_DOMINION_ROOT is not set"""
        from bridge_tools.bcse.rewriters import rewrite_localhost_to_forge
        
        old_forge = os.environ.get("FORGE_DOMINION_ROOT")
        os.environ.pop("FORGE_DOMINION_ROOT", None)
        
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                changed = rewrite_localhost_to_forge([tmpdir])
                assert changed == 0, "Should return 0 when FORGE_DOMINION_ROOT not set"
        finally:
            if old_forge:
                os.environ["FORGE_DOMINION_ROOT"] = old_forge


class TestCoder:
    """Test patch proposal generator"""

    def test_coder_import(self):
        """Test that coder module can be imported"""
        from bridge_tools.bcse import coder
        assert coder is not None

    def test_propose_patch(self):
        """Test patch proposal generation"""
        from bridge_tools.bcse.coder import propose_patch
        
        with tempfile.TemporaryDirectory() as tmpdir:
            original = "x = 1\n"
            updated = "x = 2\n"
            
            patch_file = propose_patch("test.py", original, updated, out_dir=tmpdir)
            
            assert Path(patch_file).exists(), "Patch file should be created"
            content = Path(patch_file).read_text()
            assert "Dominion-Signature" in content, "Patch should have signature"


class TestAutofix:
    """Test autofix infrastructure"""

    def test_autofix_import(self):
        """Test that autofix package can be imported"""
        from bridge_tools.bcse import autofix
        assert autofix is not None

    def test_generate_patch(self):
        """Test patch generation"""
        from bridge_tools.bcse.autofix import generate_patch
        
        old = "line1\nline2\n"
        new = "line1\nline2 modified\n"
        
        patch = generate_patch(old, new, "test.py")
        assert "---" in patch, "Should contain diff header"
        assert "+++" in patch, "Should contain diff header"

    def test_list_pending_patches(self):
        """Test listing pending patches"""
        from bridge_tools.bcse.autofix import list_pending_patches
        
        patches = list_pending_patches()
        assert isinstance(patches, list)

    def test_explain_patch(self):
        """Test patch explanation"""
        from bridge_tools.bcse.autofix import explain_patch
        
        with tempfile.TemporaryDirectory() as tmpdir:
            patch_file = Path(tmpdir) / "test.patch"
            patch_content = """--- a/test.py
+++ b/test.py
@@ -1,1 +1,1 @@
-old line
+new line
# Dominion-Signature: TEST
"""
            patch_file.write_text(patch_content)
            
            explanation = explain_patch(str(patch_file))
            assert explanation is not None
            assert "Signature: TEST" in explanation


class TestProdsim:
    """Test production simulation module"""

    def test_prodsim_import(self):
        """Test that prodsim module can be imported"""
        from bridge_tools.bcse import prodsim
        assert prodsim is not None

    def test_check_cors_with_https(self):
        """Test CORS check with valid https origins"""
        from bridge_tools.bcse.prodsim import check_cors
        
        result = check_cors("https://example.com,https://other.com")
        assert result == 0, "Should pass with https origins"

    def test_check_cors_without_https(self):
        """Test CORS check without https origins"""
        from bridge_tools.bcse.prodsim import check_cors
        
        result = check_cors("http://example.com")
        assert result == 1, "Should fail without https origins"

    def test_check_cors_empty(self):
        """Test CORS check with empty origins"""
        from bridge_tools.bcse.prodsim import check_cors
        
        result = check_cors("")
        assert result == 1, "Should fail with empty origins"
