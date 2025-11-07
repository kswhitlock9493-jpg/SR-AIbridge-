# Bridge Code Super-Engine (BCSE) Makefile
# Convenience commands for quality gates

.PHONY: init analyze fix test help

help:
	@echo "🜂 Bridge Code Super-Engine (BCSE) - Available Commands"
	@echo ""
	@echo "  make init     - Install development dependencies"
	@echo "  make analyze  - Run comprehensive quality analysis"
	@echo "  make fix      - Auto-fix style and simple issues"
	@echo "  make test     - Run tests with coverage"
	@echo ""

init:
	@echo "📦 Installing development dependencies..."
	pip install -r requirements-dev.txt
	@echo "📦 Installing frontend dependencies..."
	npm --prefix bridge-frontend ci

analyze:
	@echo "🜂 Running BCSE quality analysis..."
	python -m bridge_tools.bcse.cli analyze

fix:
	@echo "🔧 Running BCSE auto-fix..."
	python -m bridge_tools.bcse.cli fix

test:
	@echo "🧪 Running tests..."
	pytest -q
