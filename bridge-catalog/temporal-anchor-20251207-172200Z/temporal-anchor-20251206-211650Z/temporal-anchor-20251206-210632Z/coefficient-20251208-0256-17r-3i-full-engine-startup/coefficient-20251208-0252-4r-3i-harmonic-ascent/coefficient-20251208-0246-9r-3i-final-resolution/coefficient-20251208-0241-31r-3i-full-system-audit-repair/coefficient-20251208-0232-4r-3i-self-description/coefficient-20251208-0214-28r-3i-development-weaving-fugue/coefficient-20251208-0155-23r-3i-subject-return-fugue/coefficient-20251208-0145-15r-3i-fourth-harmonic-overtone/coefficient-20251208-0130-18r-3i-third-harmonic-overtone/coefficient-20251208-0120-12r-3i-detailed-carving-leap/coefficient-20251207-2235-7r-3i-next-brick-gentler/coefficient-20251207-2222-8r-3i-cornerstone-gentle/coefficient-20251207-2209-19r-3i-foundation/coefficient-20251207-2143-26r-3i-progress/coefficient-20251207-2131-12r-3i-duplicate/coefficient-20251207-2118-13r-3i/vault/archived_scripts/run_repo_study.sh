#!/bin/bash
# Quick launcher for the repository study script

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "╔═══════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                           ║"
echo "║            SR-AIbridge Repository Study Quick Launcher                    ║"
echo "║                                                                           ║"
echo "╚═══════════════════════════════════════════════════════════════════════════╝"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "❌ Error: Python is not installed or not in PATH"
    exit 1
fi

# Use python3 if available, otherwise python
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

echo "🐍 Using Python: $($PYTHON_CMD --version)"
echo ""

# Check if dependencies are installed
echo "📦 Checking dependencies..."
if ! $PYTHON_CMD -c "import fastapi" 2>/dev/null; then
    echo "⚠️  Dependencies not found. Installing..."
    $PYTHON_CMD -m pip install -q -r requirements.txt
    echo "✓ Dependencies installed"
else
    echo "✓ Dependencies already installed"
fi
echo ""

# Run the study script
echo "🚀 Launching repository study..."
echo ""
$PYTHON_CMD study_repo_with_engines.py

exit_code=$?

if [ $exit_code -eq 0 ]; then
    echo ""
    echo "╔═══════════════════════════════════════════════════════════════════════════╗"
    echo "║                         Study Completed Successfully! ✓                   ║"
    echo "╚═══════════════════════════════════════════════════════════════════════════╝"
    echo ""
    echo "📄 Check REPO_STUDY_REPORT.json for detailed results"
    echo "📚 See REPO_STUDY_GUIDE.md for usage documentation"
    echo ""
else
    echo ""
    echo "❌ Study script exited with error code: $exit_code"
    exit $exit_code
fi
