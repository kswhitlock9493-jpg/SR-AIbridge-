#!/usr/bin/env python3
"""
HTML Compiler for the Repo Codex Engine.

This module compiles the repository into a styled HTML format with
animated Forge Seal and Dominion Glow effects.
Can be run as a standalone script or imported as a module.
"""
import markdown
import os
from datetime import datetime, timezone


def build_html():
    """Build a styled HTML book from the markdown repo book."""
    src = "codex/output/repo_book.md"
    dst = "codex/output/repo_book.html"

    if not os.path.exists(src):
        raise FileNotFoundError("repo_book.md not found. Run markdown_compiler first.")

    with open(src, "r", encoding="utf-8") as f:
        md = f.read()

    html_body = markdown.markdown(md, extensions=["fenced_code", "tables", "toc"])

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Book of the Repo</title>
<style>
@keyframes forgeGlow {{
  0%   {{ text-shadow: 0 0 6px #00ffaa; }}
  50%  {{ text-shadow: 0 0 20px #00ffaa, 0 0 40px #00ffaa66; }}
  100% {{ text-shadow: 0 0 6px #00ffaa; }}
}}
@keyframes sealPulse {{
  0%   {{ transform: rotate(0deg) scale(1); opacity: 0.9; }}
  50%  {{ transform: rotate(180deg) scale(1.06); opacity: 1; }}
  100% {{ transform: rotate(360deg) scale(1); opacity: 0.9; }}
}}

body {{
  font-family: 'JetBrains Mono', monospace;
  background: radial-gradient(circle at 50% 10%, #001a10 0%, #000 80%);
  color: #aefdd0;
  margin: 0;
  padding: 2rem;
  line-height: 1.5;
}}
h1, h2, h3, h4 {{
  color: #00ffaa;
  animation: forgeGlow 3s infinite ease-in-out;
  margin-top: 1.4rem;
}}
a {{ color: #00ffd0; }}

pre, code {{
  background: #0b0b0b;
  color: #8effb8;
  border-radius: 6px;
  padding: 0.3em 0.5em;
}}

hr {{
  border: none;
  height: 1px;
  background: linear-gradient(to right, #00ffaa 20%, transparent 80%);
  margin: 1.5rem 0;
}}

.container {{
  max-width: 960px;
  margin: auto;
}}

#forgeSeal {{
  width: 120px;
  height: 120px;
  margin: 0 auto 1rem;
  border-radius: 50%;
  border: 2px solid #00ffaa;
  animation: sealPulse 8s infinite linear;
  box-shadow: 0 0 20px #00ffaa60;
  background: conic-gradient(from 0deg, #00ffaa20, #00ffaa, #00ffaa20);
}}

footer {{
  margin-top: 3rem;
  text-align: center;
  font-size: 0.85em;
  color: #0f0;
}}

nav {{
  background: rgba(0,255,180,0.05);
  border: 1px solid #00ffaa30;
  padding: 1rem;
  border-radius: 10px;
  margin-bottom: 2rem;
}}
nav h2 {{
  margin-bottom: 0.5rem;
}}
nav ul {{
  list-style-type: none;
  padding-left: 0;
}}
nav li {{
  margin: 0.3rem 0;
}}
</style>
</head>
<body>
<div class="container">
  <div id="forgeSeal"></div>
  <h1 style="text-align:center;">SR-AIBridge — The Book of the Repo</h1>
  <nav>
    <h2>📚 Book of the Repo</h2>
    <p><em>Auto-generated on {datetime.now(timezone.utc).isoformat()} UTC</em></p>
    <ul>
      <li><a href="#brain-truth-engine-summary">🧠 Truth Engine</a></li>
      <li><a href="#documentations">📄 Documentation</a></li>
      <li><a href="#blueprint-overview">🧬 Blueprint</a></li>
    </ul>
  </nav>
  {html_body}
  <footer>
    <p>SR-AIBridge — Sovereign Runtime Codex © {datetime.now(timezone.utc).year}</p>
  </footer>
</div>
</body>
</html>
"""

    with open(dst, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"🌐 HTML Book generated → {dst}")


if __name__ == "__main__":
    build_html()
