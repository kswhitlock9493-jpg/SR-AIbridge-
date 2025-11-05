#!/bin/bash
# Render.com Quantum Security Service
# This script runs quantum security checks on Render's free tier
# Triggered by webhook from GitHub Actions

set -e

echo "🜂 Starting Quantum Security Check on Render.com"
echo "=================================================="

# Environment variables expected:
# - GITHUB_REPO: Repository URL
# - GITHUB_REF: Branch/commit to check
# - GITHUB_TOKEN: GitHub token for API access
# - WEBHOOK_CALLBACK_URL: URL to send results back to

# Clone repository
if [ -n "$GITHUB_REPO" ]; then
    echo "Cloning repository: $GITHUB_REPO"
    git clone --depth 1 --branch "${GITHUB_REF:-main}" "$GITHUB_REPO" /tmp/repo
    cd /tmp/repo
else
    echo "Using pre-cloned repository"
    cd /app
fi

# Install dependencies (cached by Render)
echo "Installing Python dependencies..."
pip install -r bridge_backend/requirements.txt

# Set environment variables for quantum checks
export FORGE_DOMINION_MODE="${FORGE_DOMINION_MODE:-sovereign}"
export FORGE_DOMINION_VERSION="${FORGE_DOMINION_VERSION:-1.9.7s}"
export ENVIRONMENT="${ENVIRONMENT:-production}"

# Run quantum security orchestrator
echo "Running Quantum Predeploy Orchestrator..."
python3 bridge_backend/runtime/quantum_predeploy_orchestrator.py

# Check results
if [ -f .alik/predeploy_report.json ]; then
    echo "✅ Quantum security check completed"
    
    # Send results back to GitHub via webhook if callback URL provided
    if [ -n "$WEBHOOK_CALLBACK_URL" ]; then
        echo "Sending results to callback URL..."
        curl -X POST "$WEBHOOK_CALLBACK_URL" \
            -H "Content-Type: application/json" \
            -H "Authorization: Bearer $GITHUB_TOKEN" \
            -d @.alik/predeploy_report.json
    fi
    
    # Extract critical failures
    if [ -f .github/scripts/check_critical_failures.py ]; then
        python3 .github/scripts/check_critical_failures.py
    fi
else
    echo "❌ No security report generated"
    exit 1
fi

echo "=================================================="
echo "🜂 Quantum Security Check Complete"
