"""
Test suite for the Repo Codex Engine.

Tests the truth engine, parser engine, blueprint engine, and compilers.
"""
import pytest
import os
import json

from codex.truth_engine import gather_meta, validate_facts
from codex.parser_engine import parse_docs
from codex.blueprint_engine import build_blueprint


class TestTruthEngine:
    """Test the Truth Engine functionality."""

    def test_gather_meta(self):
        """Test gathering metadata from YAML files."""
        meta = gather_meta()
        assert isinstance(meta, dict)
        # Should find at least the codex/manifest.yaml and bridge.runtime.yaml
        assert len(meta) > 0

    def test_validate_facts(self):
        """Test fact validation and deduplication."""
        meta = gather_meta()
        facts = validate_facts(meta)
        assert isinstance(facts, dict)
        # Each fact should have key, value, and source
        for sig, fact in facts.items():
            assert "key" in fact
            assert "value" in fact
            assert "source" in fact
            assert len(sig) == 12  # SHA256 hash truncated to 12 chars


class TestParserEngine:
    """Test the Parser Engine functionality."""

    def test_parse_docs(self):
        """Test parsing markdown files."""
        docs = parse_docs()
        assert isinstance(docs, list)
        # Should find multiple markdown files in the repo
        assert len(docs) > 0
        
        # Check structure of parsed docs
        for doc in docs:
            assert "file" in doc
            assert "headers" in doc
            assert "content" in doc
            assert isinstance(doc["headers"], list)
            assert isinstance(doc["content"], str)


class TestBlueprintEngine:
    """Test the Blueprint Engine functionality."""

    def test_build_blueprint(self):
        """Test building dependency blueprint."""
        blueprint = build_blueprint()
        assert isinstance(blueprint, dict)
        assert "modules" in blueprint
        assert "relations" in blueprint
        assert isinstance(blueprint["modules"], list)
        
        # Should find Python files in the repo
        assert len(blueprint["modules"]) > 0
        
        # Check module structure
        for module in blueprint["modules"]:
            assert "file" in module
            assert "imports" in module
            assert isinstance(module["imports"], list)


class TestCompilers:
    """Test the compiler functionality."""

    def test_json_compiler_output(self):
        """Test that JSON compiler creates valid output."""
        from codex.compiler import compile_codex
        
        # Run the compiler
        compile_codex()
        
        # Check that output file exists
        output_path = "codex/output/repo_book.json"
        assert os.path.exists(output_path)
        
        # Verify JSON is valid
        with open(output_path, "r") as f:
            book = json.load(f)
        
        assert "truth" in book
        assert "documentation" in book
        assert "blueprint" in book

    def test_markdown_compiler_output(self):
        """Test that Markdown compiler creates valid output."""
        from codex.markdown_compiler import compile_markdown
        
        # Run the compiler
        compile_markdown()
        
        # Check that output file exists
        output_path = "codex/output/repo_book.md"
        assert os.path.exists(output_path)
        
        # Verify markdown has expected sections
        with open(output_path, "r") as f:
            content = f.read()
        
        assert "# 📘 The Book of the Repo" in content
        assert "## 🧠 Truth Engine Summary" in content
        assert "## 📄 Documentation Index" in content
        assert "## 🧬 Blueprint Overview" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
