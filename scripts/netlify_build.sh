#!/usr/bin/env bash
set -euo pipefail

# Error reporting function
report_error() {
  local error_msg="$1"
  local exit_code="${2:-1}"
  echo "❌ BUILD FAILED: $error_msg" >&2
  echo "Exit code: $exit_code" >&2
  echo "Timestamp: $(date -u +"%Y-%m-%dT%H:%M:%SZ")" >&2
  echo "Branch: ${BRANCH:-unknown}" >&2
  echo "Deploy ID: ${DEPLOY_ID:-unknown}" >&2
  exit "$exit_code"
}

# Set up error trap
trap 'report_error "Build script failed at line $LINENO" 1' ERR

echo "🔧 Starting Netlify build process..."
echo "Branch: ${BRANCH:-unknown}"
echo "Deploy context: ${CONTEXT:-unknown}"
echo "Working directory: $(pwd)"

# Synthesize artifacts to satisfy preview checks even for minimal branches
python3 ../scripts/synthesize_netlify_artifacts.py

# Set environment variables to skip browser downloads
export PUPPETEER_SKIP_DOWNLOAD=true
export PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=true
export NPM_CONFIG_PRODUCTION=false

# Check if frontend has a build script and build it
if [ -f "package.json" ] && jq -e '.scripts.build' package.json >/dev/null 2>&1; then
  echo "📦 Installing npm dependencies..."
  npm ci --no-audit --prefer-offline
  echo "🔨 Building frontend..."
  npm run build
else
  echo "📝 Creating minimal dist for preview..."
  mkdir -p dist
  echo "<html><body>SR-AIbridge preview</body></html>" > dist/index.html
fi

echo "✅ Netlify build complete!"
