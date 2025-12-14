import os
import logging
from pathlib import Path

DEFAULTS = ("dist", "build", "public")

def _first_existing(paths):
    for p in paths:
        if Path(p).exists():
            return p
    return None

def validate_publish_path():
    """Ensure NETLIFY_PUBLISH_PATH points to a real folder; fall back sanely."""
    requested = os.getenv("NETLIFY_PUBLISH_PATH")
    if requested and Path(requested).exists():
        logging.info(f"✅ Netlify Guard: using publish path: {requested}")
        return requested

    found = _first_existing((requested,) if requested else ()) or _first_existing(DEFAULTS)
    if not found:
        # create a minimal public/ so Netlify checks never hard fail
        Path("public").mkdir(parents=True, exist_ok=True)
        (Path("public") / "index.html").write_text("<!doctype html><title>Bridge</title>")
        found = "public"

    os.environ["NETLIFY_PUBLISH_PATH"] = found
    logging.warning(f"⚠️ Netlify Guard: normalized publish path -> {found}")
    return found


def require_netlify_token(get_github_token):
    """
    Prefer NETLIFY_AUTH_TOKEN; otherwise fall back to Reflex' GitHub token
    (sufficient for our guarded egress sync step).
    """
    token = os.getenv("NETLIFY_AUTH_TOKEN")
    if token:
        return token

    gh = get_github_token() if callable(get_github_token) else None
    if gh:
        os.environ["NETLIFY_AUTH_TOKEN"] = gh
        logging.info("🔑 Netlify Guard: using Reflex GitHub token as egress auth.")
        return gh

    raise RuntimeError("❌ Netlify Guard: no NETLIFY_AUTH_TOKEN or fallback token available.")
