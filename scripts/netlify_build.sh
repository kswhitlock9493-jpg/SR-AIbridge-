#!/usr/bin/env bash
set -euo pipefail

echo "🔧 Starting Netlify build process..."

# Synthesize artifacts to satisfy preview checks even for minimal branches
python3 scripts/synthesize_netlify_artifacts.py

# Set environment variables to skip browser downloads
export PUPPETEER_SKIP_DOWNLOAD=true
export PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=true
export NPM_CONFIG_PRODUCTION=false

# Check if frontend has a build script and build it
if [ -f "bridge-frontend/package.json" ] && jq -e '.scripts.build' bridge-frontend/package.json >/dev/null 2>&1; then
  echo "📦 Installing npm dependencies..."
  cd bridge-frontend
  npm ci --no-audit --prefer-offline
  echo "🔨 Building frontend..."
  npm run build
  cd ..
else
  echo "📝 Creating minimal dist for preview..."
  mkdir -p bridge-frontend/dist
  echo "<html><body>SR-AIbridge preview</body></html>" > bridge-frontend/dist/index.html
fi

echo "✅ Netlify build complete!"
