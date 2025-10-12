#!/usr/bin/env bash
set -euo pipefail

echo "🔧 Starting Netlify build process..."

# Synthesize artifacts to satisfy preview checks even for minimal branches
python3 scripts/synthesize_netlify_artifacts.py

# If you actually have a frontend build, do it; otherwise no-op:
if [ -f "package.json" ] && jq -e '.scripts.build' package.json >/dev/null 2>&1; then
  echo "📦 Installing npm dependencies..."
  npm ci
  echo "🔨 Building frontend..."
  npm run build
else
  echo "📝 Creating minimal dist for preview..."
  mkdir -p dist
  echo "<html><body>SR-AIbridge preview</body></html>" > dist/index.html
fi

echo "✅ Netlify build complete!"
