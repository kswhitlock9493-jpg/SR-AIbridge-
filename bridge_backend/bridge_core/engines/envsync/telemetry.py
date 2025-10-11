import json, logging, datetime as dt
log = logging.getLogger(__name__)

def ticket(title: str, body: str):
    # Reuse your existing diagnostics/tickets pattern
    ts = dt.datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log.warning(f"[EnvSync Ticket] {title} :: {ts}")
    # optionally write a markdown file to diagnostics tree
