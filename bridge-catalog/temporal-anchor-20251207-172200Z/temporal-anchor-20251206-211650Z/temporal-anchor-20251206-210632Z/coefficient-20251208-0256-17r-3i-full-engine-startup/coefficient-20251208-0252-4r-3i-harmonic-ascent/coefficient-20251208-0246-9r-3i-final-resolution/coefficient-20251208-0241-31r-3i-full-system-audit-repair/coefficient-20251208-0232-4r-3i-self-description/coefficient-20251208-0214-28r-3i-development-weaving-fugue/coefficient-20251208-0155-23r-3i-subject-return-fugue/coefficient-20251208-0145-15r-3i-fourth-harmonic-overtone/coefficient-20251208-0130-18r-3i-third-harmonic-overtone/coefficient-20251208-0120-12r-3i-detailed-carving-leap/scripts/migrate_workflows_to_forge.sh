#!/bin/bash
#
# Workflow Migration Helper for Forge Dominion Token Forge
# Version: 1.9.7s
#
# This script helps identify workflows that need to be migrated to use
# the Sovereign Dominion Token Forge instead of hardcoded secrets.
#

set -e

echo "======================================================================="
echo "🜂 Forge Dominion Workflow Migration Helper v1.9.7s"
echo "======================================================================="
echo ""

WORKFLOW_DIR=".github/workflows"

if [ ! -d "$WORKFLOW_DIR" ]; then
    echo "❌ Error: $WORKFLOW_DIR directory not found"
    exit 1
fi

echo "Scanning workflows for hardcoded secrets..."
echo ""

# Find workflows using hardcoded secrets (excluding FORGE_DOMINION_ROOT and GITHUB_TOKEN)
# Use process substitution and command substitution to preserve variable state
NETLIFY_COUNT=0
RENDER_COUNT=0
GITHUB_COUNT=0
OTHER_COUNT=0

echo "📋 Workflows using NETLIFY_AUTH_TOKEN from secrets:"
while IFS= read -r file; do
    [ -z "$file" ] && continue
    echo "  - $(basename "$file")"
    NETLIFY_COUNT=$((NETLIFY_COUNT + 1))
done < <(grep -l "NETLIFY_AUTH_TOKEN.*secrets\." "$WORKFLOW_DIR"/*.yml 2>/dev/null || true)
echo ""

echo "📋 Workflows using RENDER_API_KEY from secrets:"
while IFS= read -r file; do
    [ -z "$file" ] && continue
    echo "  - $(basename "$file")"
    RENDER_COUNT=$((RENDER_COUNT + 1))
done < <(grep -l "RENDER_API_KEY.*secrets\." "$WORKFLOW_DIR"/*.yml 2>/dev/null || true)
echo ""

echo "📋 Workflows using GITHUB_TOKEN from secrets (excluding auto-provided):"
while IFS= read -r file; do
    [ -z "$file" ] && continue
    echo "  - $(basename "$file")"
    GITHUB_COUNT=$((GITHUB_COUNT + 1))
done < <(grep -l "GITHUB_TOKEN.*secrets\." "$WORKFLOW_DIR"/*.yml 2>/dev/null | grep -v "secrets.GITHUB_TOKEN" || true)
echo ""

echo "📋 Workflows using other API tokens/keys from secrets:"
while IFS= read -r file; do
    [ -z "$file" ] && continue
    echo "  - $(basename "$file")"
    OTHER_COUNT=$((OTHER_COUNT + 1))
done < <(grep -E "API_TOKEN|API_KEY|AUTH_TOKEN" "$WORKFLOW_DIR"/*.yml 2>/dev/null | \
    grep "secrets\." | \
    grep -v "FORGE_DOMINION_ROOT" | \
    grep -v "GITHUB_TOKEN" | \
    cut -d: -f1 | sort -u || true)
echo ""

TOTAL_COUNT=$((NETLIFY_COUNT + RENDER_COUNT + GITHUB_COUNT + OTHER_COUNT))

echo "======================================================================="
echo "Migration Instructions:"
echo "======================================================================="
echo ""
echo "To migrate a workflow to use Forge Dominion:"
echo ""
echo "1. Add the Forge Dominion setup step:"
echo "   - name: Setup Forge Dominion"
echo "     id: forge"
echo "     uses: ./.github/actions/forge-dominion-setup"
echo "     with:"
echo "       forge-dominion-root: \${{ secrets.FORGE_DOMINION_ROOT }}"
echo "       providers: 'netlify,render,github'"
echo ""
echo "2. Replace secret references with action outputs:"
echo "   # OLD:"
echo "   env:"
echo "     NETLIFY_AUTH_TOKEN: \${{ secrets.NETLIFY_AUTH_TOKEN }}"
echo ""
echo "   # NEW:"
echo "   env:"
echo "     NETLIFY_AUTH_TOKEN: \${{ steps.forge.outputs.netlify-token }}"
echo ""
echo "3. Keep non-secret variables as vars:"
echo "   NETLIFY_SITE_ID: \${{ vars.NETLIFY_SITE_ID }}"
echo "   RENDER_SERVICE_ID: \${{ vars.RENDER_SERVICE_ID }}"
echo ""
echo "======================================================================="
echo "Example: See .github/workflows/bridge_autodeploy.yml"
echo "======================================================================="
echo ""

if [ "$TOTAL_COUNT" -eq 0 ]; then
    echo "✅ No workflows with hardcoded secrets found!"
    echo "🜂 All workflows are using Forge Dominion Token Forge."
else
    echo "⚠️  Found $TOTAL_COUNT workflow(s) that may need migration:"
    echo "   - NETLIFY_AUTH_TOKEN: $NETLIFY_COUNT"
    echo "   - RENDER_API_KEY: $RENDER_COUNT"
    echo "   - GITHUB_TOKEN: $GITHUB_COUNT"
    echo "   - Other tokens: $OTHER_COUNT"
    echo ""
    echo "   Review the list above and migrate as needed."
fi

echo ""
echo "To verify environment files are clean:"
echo "  python -m bridge_backend.bridge_core.token_forge_dominion.scan_envs"
echo ""
echo "To test token minting:"
echo "  export FORGE_DOMINION_ROOT=\$(python -c \"import base64, os; print(base64.urlsafe_b64encode(os.urandom(32)).decode().rstrip('='))\")"
echo "  bash runtime/pre-deploy.dominion.sh"
echo ""
echo "======================================================================="
