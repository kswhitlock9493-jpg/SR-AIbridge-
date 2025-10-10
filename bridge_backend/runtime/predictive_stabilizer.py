import os, glob, shutil, re, logging, datetime, json
from dateutil.tz import tzutc
from bridge_backend.integrations.github_issues import maybe_create_issue

log = logging.getLogger(__name__)
TICKET_DIR = "bridge_backend/diagnostics/stabilization_tickets"
RESOLVED_DIR = os.path.join(TICKET_DIR, "resolved")
os.makedirs(TICKET_DIR, exist_ok=True)
os.makedirs(RESOLVED_DIR, exist_ok=True)

def _is_resolved(ticket_text: str) -> bool:
    """Check if a ticket's condition has been fixed"""
    # minimal but meaningful checks
    if "PORT environment variable" in ticket_text:
        return bool(os.getenv("PORT"))  # Render sets this
    if "HEARTBEAT_URL" in ticket_text:
        # heartbeat now auto-detects from RENDER_EXTERNAL_URL
        return True
    return False

def resolve_tickets():
    """Scan and resolve tickets whose conditions are now fixed"""
    for path in glob.glob(os.path.join(TICKET_DIR, "*.md")):
        with open(path, "r", encoding="utf-8") as f:
            txt = f.read()
        if _is_resolved(txt):
            base = os.path.basename(path)
            shutil.move(path, os.path.join(RESOLVED_DIR, base))
            log.info(f"stabilizer: resolved {base}")
        else:
            log.warning(f"stabilizer: ticket persists {path}")

def evaluate_stability(insights: dict):
    # Expect schema: {"stability_score": float, "most_active_modules": [["path/to/mod.py", score], ...]}
    score = float(insights.get("stability_score", 100))
    modules = insights.get("most_active_modules", [])
    if score >= 70 or not modules:
        log.info(f"stabilizer: ✅ stability acceptable ({score})")
        return {"status": "ok", "score": score}

    mod = modules[0][0]
    ts = datetime.datetime.now(tzutc()).strftime("%Y%m%dT%H%M%SZ")
    ticket_name = f"{ts}_{os.path.basename(mod)}.md"
    ticket_path = os.path.join(TICKET_DIR, ticket_name)

    md = [
        f"# Stabilization Ticket: `{mod}`",
        f"- Detected volatility: {100 - score:.2f}%",
        f"- Stability score: {score}",
        f"- Generated: {ts}",
        "## Suggested actions",
        "- Increase test coverage for change-hot paths",
        "- Reduce implicit side effects; modularize config access",
        "- Add type checks on API boundaries",
    ]
    with open(ticket_path, "w") as t:
        t.write("\n".join(md))

    log.warning(f"stabilizer: ⚠️ ticket created {ticket_path}")

    # Optional GitHub issue
    issue_title = f"[Stabilization] {mod} — volatility {100 - score:.2f}%"
    issue_body = "\n".join(md)
    gh_res = maybe_create_issue(issue_title, issue_body, labels=["stabilization","auto"])

    return {"status":"ticketed","score":score,"ticket":ticket_path,"github":gh_res}
