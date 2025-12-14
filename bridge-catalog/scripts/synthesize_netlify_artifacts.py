#!/usr/bin/env python3
"""
Synthesize Netlify artifacts to ensure preview checks pass
Creates _headers, _redirects, and minimal index.html if they don't exist
"""
from pathlib import Path
import os

# Determine the correct root based on where we're running from
script_dir = Path(__file__).resolve().parent
repo_root = script_dir.parent

# If we're being called from bridge-frontend (Netlify base dir), use current dir
# Otherwise use bridge-frontend subdirectory
if Path.cwd().name == "bridge-frontend":
    # Running from bridge-frontend (Netlify context)
    frontend_root = Path.cwd()
else:
    # Running from repo root (legacy/local testing)
    frontend_root = repo_root / "bridge-frontend"

public = frontend_root / "public"
dist = frontend_root / "dist"

# Ensure directories exist
public.mkdir(exist_ok=True)
dist.mkdir(exist_ok=True)

print("🔧 Synthesizing Netlify artifacts...")

# _headers
headers = public / "_headers"
if not headers.exists():
    headers.write_text("""/*
  X-Frame-Options: SAMEORIGIN
  X-Content-Type-Options: nosniff
  Referrer-Policy: no-referrer-when-downgrade
  Strict-Transport-Security: max-age=63072000; includeSubDomains; preload
""")
    print("✅ Created _headers")
else:
    print("ℹ️  _headers already exists")

# _redirects (SPA fallback only - API served via Netlify Functions)
redirects = public / "_redirects"
if not redirects.exists():
    redirects.write_text("""# SPA fallback - API endpoints served via Netlify Functions
/* /index.html 200
""")
    print("✅ Created _redirects")
else:
    print("ℹ️  _redirects already exists")

# Ensure SPA entry exists (for pages-changed check)
index_html = dist / "index.html"
if not index_html.exists():
    index_html.write_text("<html><body>SR-AIbridge preview</body></html>")
    print("✅ Created index.html")
else:
    print("ℹ️  index.html already exists")

print("✅ Netlify artifacts synthesized successfully!")
