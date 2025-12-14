"""
Netlify Configuration Generator
Generates _headers, _redirects, and netlify.toml files
"""

from pathlib import Path
from typing import List, Dict

from ..models import RedirectRule

DEFAULT_SECURITY_HEADERS = {
    "/*": {
        "X-Frame-Options": "SAMEORIGIN",
        "X-Content-Type-Options": "nosniff",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "geolocation=(), microphone=()",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload"
    }
}


def write_headers(root: Path, headers: Dict[str, Dict[str, str]]) -> Path:
    """Write _headers file for Netlify"""
    out = root / "_headers"
    lines = []
    for scope, kv in headers.items():
        lines.append(scope)
        for k, v in kv.items():
            lines.append(f"  {k}: {v}")
        lines.append("")
    out.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
    return out


def write_redirects(root: Path, rules: List[RedirectRule]) -> Path:
    """Write _redirects file for Netlify"""
    out = root / "_redirects"
    lines = []
    for r in rules:
        cond = " ".join([f"{k}={v}" for k, v in (r.conditions or {}).items()])
        force = "!" if r.force else ""
        lines.append(" ".join([r.from_path, r.to_path, str(r.status) + force, cond]).strip())
    out.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
    return out


def write_netlify_toml(root: Path, dist_dir: str) -> Path:
    """Write netlify.toml configuration file"""
    out = root / "netlify.toml"
    content = f"""
[build]
  publish = "{dist_dir}"
  command = "npm run build || yarn build || pnpm build"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
""".lstrip()
    out.write_text(content, encoding="utf-8")
    return out
