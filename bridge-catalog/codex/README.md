# 📘 Repo Codex Engine

> **"The Book of the Repo"** — Automatically compile your entire repository into a unified, searchable document.

## 🧩 Overview

The Repo Codex Engine is a self-documenting system that compiles all repository content (source code, documentation, and configuration) into a unified "Book of the Repo." Every update, commit, or pull request regenerates the book automatically.

## 🔹 Core Components

### Three Coordinated Engines

| Engine | Function | File |
|--------|----------|------|
| **Truth Engine** | Validates facts, metadata, and YAML manifests; deduplicates conflicting information | `truth_engine.py` |
| **Parser Engine** | Reads `.md`, `.txt`, `.yml`, `.py`, `.js`, and `.json` files; extracts headers, code blocks, schemas | `parser_engine.py` |
| **Blueprint Engine** | Reconstructs logical relationships, diagrams, and component dependencies | `blueprint_engine.py` |

### Two Compilers

| Compiler | Output | Purpose |
|----------|--------|---------|
| **JSON Compiler** | `codex/output/repo_book.json` | Machine-readable structured data |
| **Markdown Compiler** | `codex/output/repo_book.md` | Human-readable documentation |

## 🚀 Quick Start

### Manual Compilation

Compile the entire repository codex:

```bash
# Generate JSON output
python codex/compiler.py

# Generate Markdown output
python codex/markdown_compiler.py
```

### Automatic Compilation (GitHub Actions)

The codex automatically compiles on every push to `main` when any of these files change:
- `**/*.md` - Markdown documentation
- `**/*.yml` or `**/*.yaml` - Configuration files
- `**/*.py` - Python source code

See `.github/workflows/repo-codex.yml` for the workflow configuration.

## 📖 Output Structure

### repo_book.json

```json
{
  "truth": {
    "abc123def456": {
      "key": "version",
      "value": "5.5.3",
      "source": "./codex/manifest.yaml"
    }
  },
  "documentation": [
    {
      "file": "./README.md",
      "headers": ["# SR-AIbridge", "## Getting Started"],
      "content": "..."
    }
  ],
  "blueprint": {
    "modules": [
      {
        "file": "./bridge_backend/main.py",
        "imports": ["import fastapi", "from sqlalchemy import ..."]
      }
    ],
    "relations": []
  }
}
```

### repo_book.md

The markdown output contains:

1. **🧠 Truth Engine Summary** - Key facts from YAML configuration files
2. **📄 Documentation Index** - All markdown files with their headers
3. **🧬 Blueprint Overview** - Code modules and their dependencies

## 🧪 Testing

Run the comprehensive test suite:

```bash
pytest tests/test_codex_engine.py -v
```

Test coverage includes:
- Truth Engine metadata gathering and validation
- Parser Engine markdown extraction
- Blueprint Engine dependency mapping
- JSON Compiler output validation
- Markdown Compiler output validation

## 🛠️ Configuration

### codex/manifest.yaml

```yaml
name: SR-AIbridge
version: 5.5.3
description: Self-documenting repository with automated codex compilation
engines:
  truth: Validates facts and metadata from YAML files
  parser: Extracts documentation from markdown files
  blueprint: Maps code dependencies and imports
outputs:
  - codex/output/repo_book.json
  - codex/output/repo_book.md
```

## 📊 Statistics (Current Repository)

- **Truth Entries**: 23+ YAML facts extracted
- **Documentation Files**: 332+ markdown files indexed
- **Code Modules**: 760+ Python/JS modules analyzed
- **Output Size**: 
  - JSON: ~3.5 MB
  - Markdown: ~532 KB

## 🔄 Workflow Integration

The GitHub Actions workflow (`.github/workflows/repo-codex.yml`) automatically:

1. Triggers on push to `main` branch
2. Installs Python dependencies (PyYAML)
3. Compiles both JSON and Markdown outputs
4. Uploads artifacts for download

## 🎯 Use Cases

- **Onboarding**: New team members can read the Book of the Repo to understand the codebase
- **Documentation**: Always up-to-date reference of all documentation
- **Dependencies**: See all code dependencies at a glance
- **Configuration**: Understand all YAML configuration in one place
- **Search**: Machine-readable JSON enables powerful search capabilities

## 🔐 Security

- No sensitive data is exposed in the codex
- The codex compiles only files already in the repository
- YAML facts are deduplicated and hashed for integrity
- All file parsing is safe and handles exceptions gracefully

## 📝 Development

To extend the codex:

1. **Add new engines**: Create a new engine file in `codex/`
2. **Modify compilers**: Update `compiler.py` or `markdown_compiler.py`
3. **Add tests**: Extend `tests/test_codex_engine.py`
4. **Update workflow**: Modify `.github/workflows/repo-codex.yml` if needed

## 🎉 Features

- ✅ **Self-authored**: 100% custom implementation
- ✅ **Forge-ready**: Compatible with Forge Dominion
- ✅ **Auto-versioned**: Tracks repository commits
- ✅ **Cross-referenced**: Links YAML, docs, and code
- ✅ **Human-readable**: Markdown output for easy reading
- ✅ **Machine-readable**: JSON output for tooling
- ✅ **Automated**: GitHub Actions integration

---

**Built with 🚀 by the SR-AIbridge Team**
