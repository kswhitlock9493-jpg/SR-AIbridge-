# Bridge Code Super-Engine (BCSE) Makefile
# Convenience commands for quality gates

.PHONY: init analyze fix test gates improve prove rewrite review-patches apply-patches help

help:
	@echo "🜂 Bridge Code Super-Engine (BCSE) - Available Commands"
	@echo ""
	@echo "  make init            - Install development dependencies"
	@echo "  make analyze         - Run comprehensive quality analysis"
	@echo "  make fix             - Auto-fix style and simple issues"
	@echo "  make test            - Run tests with coverage"
	@echo "  make gates           - Show all quality gates (placeholder mode)"
	@echo ""
	@echo "🜂 BCSE++ (v2) Commands:"
	@echo "  make improve         - Apply safe AST transforms"
	@echo "  make prove           - Run full production readiness proof"
	@echo "  make rewrite         - Rewrite localhost to Forge Dominion"
	@echo "  make review-patches  - Review pending patches"
	@echo "  make apply-patches   - Apply approved patches"
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

gates:
	@echo "👁️  Revealing quality gates..."
	python -m bridge_tools.bcse.cli gates

improve:
	@echo "🔧 Running BCSE code improvements..."
	python -m bridge_tools.bcse.cli improve

prove:
	@echo "✅ Running production proof..."
	ENVIRONMENT=production CORS_ALLOW_ALL=false DEBUG=false \
	ALLOWED_ORIGINS=https://sr-aibridge.netlify.app \
	FORGE_DOMINION_ROOT=$${FORGE_DOMINION_ROOT} \
	python -m bridge_tools.bcse.cli prove

rewrite:
	@echo "🔁 Rewriting localhost to Forge..."
	python -m bridge_tools.bcse.cli rewrite

review-patches:
	@echo "📋 Reviewing pending patches..."
	@ls -la bridge_tools/bcse/autofix/patch_queue/*.patch 2>/dev/null || echo "No patches pending"

apply-patches:
	@echo "✅ Applying approved patches..."
	@for patch in bcse_autofixes/*.patch; do \
		[ -f "$$patch" ] && patch -p1 < "$$patch" && echo "Applied: $$patch"; \
	done
