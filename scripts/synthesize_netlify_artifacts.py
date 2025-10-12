#!/usr/bin/env python3
"""
Synthesize Netlify artifacts to ensure preview checks pass
Creates _headers, _redirects, and minimal index.html if they don't exist
"""
from pathlib import Path

root = Path(__file__).resolve().parents[1]
public = root / "public"
dist = root / "dist"

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

# _redirects (proxy + SPA fallback)
redirects = public / "_redirects"
if not redirects.exists():
    redirects.write_text("""/api/* https://sr-aibridge.onrender.com/:splat 200!
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
