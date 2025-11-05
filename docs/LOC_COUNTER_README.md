# Lines of Code Counter - Usage Guide

This directory contains tools for counting lines of code (LOC) in the SR-AIbridge project.

## Quick Summary

**Total Lines of Code: ~48,100**

### By Language (excluding dependencies):
- **Python**: ~21,000 lines (44%)
- **Markdown**: ~9,500 lines (20%)
- **JavaScript/TypeScript**: ~5,300 lines (11%)
- **JSON**: ~6,100 lines (13%)
- **CSS**: ~1,900 lines (4%)
- **Other**: ~3,700 lines (8%)

## Tools Available

### 1. Comprehensive LOC Counter (Recommended)

**Script:** `count_loc.py`

Generates a detailed LOC report with:
- Summary statistics by file type
- Breakdown showing percentage distribution
- Top files by category
- Full file list with line counts
- Markdown report saved to `LOC_REPORT.md`

**Usage:**
```bash
python3 count_loc.py
```

**Output:**
- Console: Detailed formatted report
- File: `LOC_REPORT.md` with full breakdown

### 2. Quick LOC Counter

**Script:** `LOC counter` (bash script)

Provides a quick summary without detailed breakdown.

**Usage:**
```bash
bash "LOC counter"
```

**Output:**
```
PY  : 20963
JSX : 5327
SH  : 675
YML : 525
MD  : 9941
SQL : 491
```

## What's Counted

The LOC counter includes:
- All source code files (.py, .js, .jsx, .ts, .tsx)
- Documentation (.md)
- Configuration files (.yml, .yaml, .toml, .json)
- Scripts (.sh, .bash)
- Database files (.sql)
- Stylesheets (.css)
- HTML templates (.html)

## What's Excluded

The following are excluded from counts:
- `node_modules/` - NPM dependencies
- `__pycache__/` - Python bytecode cache
- `.git/` - Git repository metadata
- `dist/`, `build/` - Build artifacts
- `.venv/`, `venv/` - Python virtual environments
- `.pytest_cache/` - Test cache
- `dock_day_exports/` - Export data

## Report Structure

The comprehensive report (`LOC_REPORT.md`) includes:

1. **Summary**: Total files and lines
2. **Breakdown by File Type**: Table showing distribution
3. **Detailed File List**: All files organized by category with line counts

## Project Composition

Based on the latest count:

### Backend (Python)
- **Core Engines**: ~12,000 lines
  - Leviathan, Recovery, Cascade, Truth, Creativity, etc.
- **API Routes**: ~5,000 lines
- **Support Modules**: ~4,000 lines

### Frontend (JavaScript/React)
- **Components**: ~4,500 lines
- **API Client**: ~500 lines
- **Utilities**: ~340 lines

### Documentation
- **README & Guides**: ~3,500 lines
- **API Docs**: ~2,000 lines
- **Architecture Docs**: ~4,000 lines

### Infrastructure
- **Workflows & Config**: ~650 lines
- **Database Scripts**: ~500 lines
- **Shell Scripts**: ~680 lines

## Maintenance

The LOC counter should be run periodically to track project growth:

```bash
# Run comprehensive count and save report
python3 count_loc.py

# Quick check
bash "LOC counter"
```

## Notes

- Line counts include blank lines and comments
- The actual "code" lines may be lower than reported
- Package files (`package-lock.json`) can skew JSON counts
- Binary files and images are detected but not line-counted

## Last Updated

**Date**: 2025-10-05  
**Total LOC**: 48,100 lines  
**Total Files**: 266 files
