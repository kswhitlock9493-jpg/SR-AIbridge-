#!/bin/bash
# ARIE CI Script
# Runs ARIE integrity checks in CI/CD pipeline

set -e

REPO_ROOT=$(git rev-parse --show-toplevel)
cd "$REPO_ROOT"

# Detect environment
IS_PR=${GITHUB_EVENT_NAME:-}
BRANCH=${GITHUB_REF_NAME:-$(git branch --show-current)}
IS_MAIN=$([[ "$BRANCH" == "main" ]] && echo "true" || echo "false")

echo "🔍 ARIE CI Check"
echo "  Branch: $BRANCH"
echo "  Is PR: ${IS_PR:-false}"
echo "  Is Main: $IS_MAIN"

# On PRs: read-only scan
if [[ "$IS_PR" == "pull_request" ]]; then
    echo ""
    echo "📋 Running read-only scan (PR mode)..."
    python3 -m bridge_backend.cli.ariectl scan --dry-run --verbose
    EXIT_CODE=$?
    
    if [ $EXIT_CODE -eq 0 ]; then
        echo "✅ ARIE scan passed"
    else
        echo "❌ ARIE scan failed"
        exit $EXIT_CODE
    fi

# On main: can apply fixes if admiral token available
elif [[ "$IS_MAIN" == "true" ]] && [[ -n "${ARIE_ADMIRAL_TOKEN:-}" ]]; then
    echo ""
    echo "🔧 Running with fix capability (main + admiral token)..."
    
    # First scan
    python3 -m bridge_backend.cli.ariectl scan --policy SAFE_EDIT --dry-run
    
    # Check if ARIE_AUTO_FIX is enabled
    if [[ "${ARIE_AUTO_FIX_ON_DEPLOY_SUCCESS:-false}" == "true" ]]; then
        echo ""
        echo "🔧 Auto-fix enabled, applying SAFE_EDIT fixes..."
        python3 -m bridge_backend.cli.ariectl apply --policy SAFE_EDIT --yes || true
    else
        echo ""
        echo "ℹ️  Auto-fix disabled (set ARIE_AUTO_FIX_ON_DEPLOY_SUCCESS=true to enable)"
    fi

# On main without token: read-only
else
    echo ""
    echo "📋 Running read-only scan (no admiral token)..."
    python3 -m bridge_backend.cli.ariectl scan --dry-run
    EXIT_CODE=$?
    
    if [ $EXIT_CODE -eq 0 ]; then
        echo "✅ ARIE scan passed"
    else
        echo "❌ ARIE scan failed"
        exit $EXIT_CODE
    fi
fi

echo ""
echo "✅ ARIE CI check complete"
exit 0
