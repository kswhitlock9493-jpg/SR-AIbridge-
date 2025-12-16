#!/usr/bin/env bash
set -euo pipefail

echo "↪ Applying npm registry fallback/mirrors for known namespaces…"

# Speed up and avoid audit noise
npm set audit false
npm set fund false

# Prefer main registry but allow scoped mirrors (example mirrors)
npm set @netlify:registry=https://registry.npmjs.org/
npm set @vitejs:registry=https://registry.npmjs.org/
npm set @rollup:registry=https://registry.npmjs.org/

# Retry knobs for flaky networks
npm set fetch-retries 4
npm set fetch-retry-factor 3
npm set fetch-retry-maxtimeout 60000
npm set fetch-retry-mintimeout 1000

echo "✅ Registry fallback configured."
