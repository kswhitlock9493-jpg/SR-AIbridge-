#!/bin/bash
# Example script to generate a valid FORGE_DOMINION_ROOT variable
# Usage: ./generate_forge_root.sh [dev|prod] [seal]

set -e

ENV="${1:-dev}"
SEAL="${2:-dev-seal}"

# Generate current epoch
EPOCH=$(date +%s)

# Generate HMAC-SHA256 signature
MESSAGE="dominion://sovereign.bridge|${ENV}|${EPOCH}"
SIG=$(echo -n "${MESSAGE}" | openssl dgst -sha256 -hmac "${SEAL}" | cut -d' ' -f2)

# Construct the FORGE_DOMINION_ROOT
FORGE_ROOT="dominion://sovereign.bridge?env=${ENV}&epoch=${EPOCH}&sig=${SIG}"

echo "============================================"
echo "FORGE_DOMINION_ROOT Generated"
echo "============================================"
echo ""
echo "Environment: ${ENV}"
echo "Epoch: ${EPOCH}"
echo "Signature: ${SIG}"
echo ""
echo "Export this variable:"
echo "export FORGE_DOMINION_ROOT=\"${FORGE_ROOT}\""
echo ""
echo "Also set the seal:"
echo "export DOMINION_SEAL=\"${SEAL}\""
echo ""
echo "============================================"
