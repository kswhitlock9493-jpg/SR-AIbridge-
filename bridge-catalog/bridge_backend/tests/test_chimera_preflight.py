"""
Test Chimera Preflight Engine (v1.9.6r)
Tests for autonomous deploy healing
"""

import unittest
import asyncio
from pathlib import Path
import tempfile
import shutil
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestChimeraPreflight(unittest.TestCase):
    """Test Chimera preflight functionality"""
    
    def test_chimera_preflight_generates_files(self):
        """Test that preflight generates all required files"""
        from engines.chimera.core import ChimeraEngine
        
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            
            # Create a mock dist directory
            (root / "frontend" / "dist").mkdir(parents=True)
            
            # Run preflight
            engine = ChimeraEngine(root)
            result = asyncio.run(engine.preflight())
            
            # Verify files were created
            self.assertTrue((root / "_headers").exists(), "_headers file should exist")
            self.assertTrue((root / "_redirects").exists(), "_redirects file should exist")
            self.assertTrue((root / "netlify.toml").exists(), "netlify.toml file should exist")
            
            # Verify result
            self.assertEqual(result["status"], "ok")
            self.assertIn("publish", result)
    
    def test_chimera_headers_format(self):
        """Test that _headers file has correct format"""
        from engines.chimera.core import ChimeraEngine
        
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "dist").mkdir()
            
            engine = ChimeraEngine(root)
            asyncio.run(engine.preflight())
            
            # Read headers file
            headers_content = (root / "_headers").read_text()
            
            # Verify security headers are present
            self.assertIn("X-Frame-Options", headers_content)
            self.assertIn("X-Content-Type-Options", headers_content)
            self.assertIn("Referrer-Policy", headers_content)
            self.assertIn("/*", headers_content)
    
    def test_chimera_redirects_format(self):
        """Test that _redirects file has correct format"""
        from engines.chimera.core import ChimeraEngine
        
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "build").mkdir()
            
            engine = ChimeraEngine(root)
            asyncio.run(engine.preflight())
            
            # Read redirects file
            redirects_content = (root / "_redirects").read_text()
            
            # Verify redirects are present
            self.assertIn("/api/*", redirects_content)
            self.assertIn("/*", redirects_content)
            self.assertIn("/index.html", redirects_content)
    
    def test_chimera_netlify_toml_format(self):
        """Test that netlify.toml has correct format"""
        from engines.chimera.core import ChimeraEngine
        
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "frontend" / "build").mkdir(parents=True)
            
            engine = ChimeraEngine(root)
            result = asyncio.run(engine.preflight())
            
            # Read netlify.toml
            toml_content = (root / "netlify.toml").read_text()
            
            # Verify build configuration
            self.assertIn("[build]", toml_content)
            self.assertIn("publish", toml_content)
            self.assertIn(result["publish"], toml_content)
            self.assertIn("[[redirects]]", toml_content)
    
    def test_chimera_detect_publish_dir(self):
        """Test that Chimera correctly detects publish directory"""
        from engines.chimera.core import ChimeraEngine
        
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            
            # Test with bridge-frontend/dist
            (root / "bridge-frontend" / "dist").mkdir(parents=True)
            engine = ChimeraEngine(root)
            detected = engine.detect_publish_dir()
            self.assertEqual(detected, "bridge-frontend/dist")
    
    def test_chimera_heal_after_failure(self):
        """Test that Chimera can heal after failure"""
        from engines.chimera.core import ChimeraEngine
        
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "dist").mkdir()
            
            engine = ChimeraEngine(root)
            
            # Simulate healing
            asyncio.run(engine.heal_after_failure("test failure"))
            
            # Verify files were regenerated
            self.assertTrue((root / "_headers").exists())
            self.assertTrue((root / "_redirects").exists())
            self.assertTrue((root / "netlify.toml").exists())
    
    def test_chimera_models(self):
        """Test Chimera models"""
        from engines.chimera.models import RedirectRule
        
        # Test basic redirect
        rule = RedirectRule(from_path="/api/*", to_path="/backend", status=200)
        self.assertEqual(rule.from_path, "/api/*")
        self.assertEqual(rule.status, 200)
        self.assertFalse(rule.force)
        
        # Test with conditions
        rule2 = RedirectRule(
            from_path="/old", 
            to_path="/new", 
            status=301, 
            force=True,
            conditions={"Country": "US"}
        )
        self.assertTrue(rule2.force)
        self.assertEqual(rule2.conditions["Country"], "US")


if __name__ == "__main__":
    unittest.main()

