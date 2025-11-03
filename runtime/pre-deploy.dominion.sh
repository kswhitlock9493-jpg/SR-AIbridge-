#!/bin/bash
#
# Pre-Deploy Dominion Hook v1.9.7s
#
# Generates ephemeral tokens for all providers before deployment.
# Called by CI/CD pipelines to mint runtime credentials.
#

set -e

echo "======================================================================="
echo "🜂 Forge Dominion Pre-Deploy v1.9.7s"
echo "======================================================================="
echo ""

# Validate FORGE_DOMINION_ROOT exists
if [ -z "$FORGE_DOMINION_ROOT" ]; then
    echo "[Dominion] ❌ FORGE_DOMINION_ROOT not set"
    echo "[Dominion] Set it with: export FORGE_DOMINION_ROOT=\$(python - <<'PY'"
    echo "import base64, os; print(base64.urlsafe_b64encode(os.urandom(32)).decode().rstrip('='))"
    echo "PY"
    echo ")"
    exit 1
fi

echo "[Dominion] ✅ FORGE_DOMINION_ROOT found"
echo "[Dominion] Root key fingerprint: ${FORGE_DOMINION_ROOT:0:8}..."
echo ""

# Set defaults
export FORGE_DOMINION_MODE="${FORGE_DOMINION_MODE:-sovereign}"
export FORGE_DOMINION_VERSION="${FORGE_DOMINION_VERSION:-1.9.7s}"
export FORGE_ENVIRONMENT="${FORGE_ENVIRONMENT:-production}"

echo "[Dominion] Mode: $FORGE_DOMINION_MODE"
echo "[Dominion] Version: $FORGE_DOMINION_VERSION"
echo "[Dominion] Environment: $FORGE_ENVIRONMENT"
echo ""

# Providers to mint tokens for
PROVIDERS=("github" "netlify" "render")

echo "[Dominion] Minting tokens for providers..."

# Mint tokens for each provider
for PROVIDER in "${PROVIDERS[@]}"; do
    echo -n "[Dominion] Forging token for $PROVIDER... "
    
    # Use Python to mint token via the quantum authority
    TOKEN_RESULT=$(python3 -c "
import json
import os
from bridge_backend.bridge_core.token_forge_dominion import QuantumAuthority, SovereignIntegration

provider = '$PROVIDER'
authority = QuantumAuthority()
sovereign = SovereignIntegration()

# Get resonance-aware TTL
environment = os.getenv('FORGE_ENVIRONMENT', 'production')
ttl_seconds = sovereign.get_resonance_aware_ttl(
    base_ttl=3600,  # 1 hour
    provider=provider,
    environment=environment
)

# Mint token
token_envelope = authority.mint_quantum_token(
    provider=provider,
    ttl_seconds=ttl_seconds
)

# Output token envelope as JSON
print(json.dumps(token_envelope))
")
    
    if [ $? -eq 0 ]; then
        echo "OK"
        
        # Store token in temporary runtime env
        # In actual deployment, these would be injected into provider configs
        export "FORGE_TOKEN_${PROVIDER^^}"="$TOKEN_RESULT"
    else
        echo "FAILED"
        exit 1
    fi
done

echo ""
echo "[Dominion] pre-deploy complete — tokens sealed."
echo ""

# Export token count for verification
export FORGE_TOKENS_MINTED="${#PROVIDERS[@]}"

echo "[Dominion] Tokens minted: $FORGE_TOKENS_MINTED"
echo "======================================================================="

exit 0
