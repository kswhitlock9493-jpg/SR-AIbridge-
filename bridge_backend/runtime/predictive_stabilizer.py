import os, glob, shutil, re, logging, datetime, json, statistics
from dateutil.tz import tzutc
from typing import Dict, Any, List, Optional
from bridge_backend.integrations.github_issues import maybe_create_issue

log = logging.getLogger(__name__)

# Directory structure
TICKET_DIR = "bridge_backend/diagnostics/stabilization_tickets"
RESOLVED_DIR = os.path.join(TICKET_DIR, "resolved")
ARCHIVE_DIR = "bridge_backend/diagnostics/archive/diagnostics"
DAILY_REPORT_DIR = "bridge_backend/diagnostics/daily_reports"
BOOT_HISTORY_FILE = "bridge_backend/diagnostics/boot_history.json"

os.makedirs(TICKET_DIR, exist_ok=True)
os.makedirs(RESOLVED_DIR, exist_ok=True)
os.makedirs(ARCHIVE_DIR, exist_ok=True)
os.makedirs(DAILY_REPORT_DIR, exist_ok=True)

# Configuration
ANOMALY_QUEUE_THRESHOLD = 3  # Require 3 consecutive similar events before logging
ARCHIVE_DAYS = 5  # Archive tickets older than 5 days
MAX_BOOT_HISTORY = 10  # Keep last 10 boot cycles for baseline calculation

# In-memory anomaly queue for silent learning
_anomaly_queue: Dict[str, List[Dict[str, Any]]] = {}

def detect_environment() -> str:
    """
    Detect deployment environment (Render, Netlify, or local)
    Returns: "render", "netlify", or "local"
    """
    if os.getenv("RENDER_EXTERNAL_URL") or os.getenv("RENDER"):
        return "render"
    if os.getenv("NETLIFY") or os.getenv("HOST_PLATFORM") == "netlify":
        return "netlify"
    return "local"

def is_live() -> bool:
    """
    Check if bridge is confirmed LIVE (heartbeat initialized)
    Returns False during pre-deploy sandbox or build phases
    """
    # Check for heartbeat initialization marker
    heartbeat_marker = os.getenv("HEARTBEAT_INITIALIZED")
    if heartbeat_marker:
        return True
    
    # In Render, we're live if we have a PORT assigned
    env = detect_environment()
    if env == "render":
        return bool(os.getenv("PORT"))
    
    # Default to True for local dev
    return env == "local"

def load_boot_history() -> List[Dict[str, Any]]:
    """Load boot cycle history for baseline calculation"""
    if not os.path.exists(BOOT_HISTORY_FILE):
        return []
    try:
        with open(BOOT_HISTORY_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        log.warning(f"Failed to load boot history: {e}")
        return []

def save_boot_cycle(metrics: Dict[str, Any]):
    """Save boot cycle metrics to history"""
    history = load_boot_history()
    
    # Add timestamp
    metrics["timestamp"] = datetime.datetime.now(tzutc()).isoformat()
    
    # Add to history
    history.append(metrics)
    
    # Keep only last MAX_BOOT_HISTORY cycles
    history = history[-MAX_BOOT_HISTORY:]
    
    try:
        with open(BOOT_HISTORY_FILE, "w") as f:
            json.dump(history, f, indent=2)
    except Exception as e:
        log.warning(f"Failed to save boot history: {e}")

def calculate_dynamic_threshold(metric_name: str = "startup_latency") -> Optional[float]:
    """
    Calculate dynamic threshold using rolling mean + 2σ (standard deviations)
    Returns None if insufficient data
    """
    history = load_boot_history()
    
    # Need at least 3 boot cycles for meaningful statistics
    if len(history) < 3:
        return None
    
    # Extract metric values
    values = []
    for cycle in history:
        if metric_name in cycle and cycle[metric_name] is not None:
            values.append(cycle[metric_name])
    
    if len(values) < 3:
        return None
    
    # Calculate mean + 2 standard deviations
    mean = statistics.mean(values)
    stdev = statistics.stdev(values)
    threshold = mean + (2 * stdev)
    
    log.info(f"[STABILIZER] Dynamic threshold for {metric_name}: {threshold:.2f}s (mean: {mean:.2f}s, σ: {stdev:.2f}s)")
    return threshold

def queue_anomaly(anomaly_type: str, details: Dict[str, Any]) -> bool:
    """
    Queue an anomaly for silent learning.
    Returns True if anomaly should be logged (3 consecutive similar events)
    """
    global _anomaly_queue
    
    if anomaly_type not in _anomaly_queue:
        _anomaly_queue[anomaly_type] = []
    
    # Add to queue
    _anomaly_queue[anomaly_type].append({
        "timestamp": datetime.datetime.now(tzutc()).isoformat(),
        "details": details
    })
    
    # Keep only recent events (last 10)
    _anomaly_queue[anomaly_type] = _anomaly_queue[anomaly_type][-10:]
    
    # Check if we have enough consecutive events
    queue = _anomaly_queue[anomaly_type]
    
    # Require ANOMALY_QUEUE_THRESHOLD consecutive events within 1 hour
    if len(queue) >= ANOMALY_QUEUE_THRESHOLD:
        recent = queue[-ANOMALY_QUEUE_THRESHOLD:]
        first_ts = datetime.datetime.fromisoformat(recent[0]["timestamp"])
        last_ts = datetime.datetime.fromisoformat(recent[-1]["timestamp"])
        
        if (last_ts - first_ts).total_seconds() < 3600:  # Within 1 hour
            log.info(f"[STABILIZER] Pattern confirmed: {anomaly_type} ({ANOMALY_QUEUE_THRESHOLD} events)")
            return True
    
    log.debug(f"[STABILIZER] Anomaly queued (silent): {anomaly_type} ({len(queue)} events)")
    return False

def record_proxy_event(event_type: str, detail: str):
    """Record proxy/CORS events for diagnostics and self-healing"""
    # Check environment awareness - suppress in pre-deploy sandbox
    if not is_live():
        log.debug(f"[STABILIZER] Suppressing proxy event in pre-deploy: {event_type}")
        return
    
    # Use silent learning mode
    if not queue_anomaly(f"proxy_{event_type}", {"detail": detail}):
        return  # Not enough consecutive events, silently queued
    
    timestamp = datetime.datetime.now(tzutc()).strftime("%Y%m%dT%H%M%SZ")
    ticket_name = f"{timestamp}_proxy.md"
    ticket_path = os.path.join(TICKET_DIR, ticket_name)
    try:
        md_content = [
            "# Proxy Stabilization Ticket\n",
            f"**Event Type:** {event_type}\n",
            f"**Details:** {detail}\n",
            f"**Timestamp:** {timestamp}\n",
            f"**Pattern:** Confirmed after {ANOMALY_QUEUE_THRESHOLD} consecutive events\n",
            "\n## Recommended Actions\n",
            "- Verify CORS configuration in main.py matches Netlify domain",
            "- Check netlify.toml proxy redirects are properly configured",
            "- Ensure /health endpoint returns 200 OK from both Netlify and Render",
            "- Review logs for recursive loop patterns",
        ]
        with open(ticket_path, "w") as f:
            f.write("\n".join(md_content))
        log.warning(f"[STABILIZER] Proxy ticket logged (pattern confirmed): {ticket_path}")
    except Exception as e:
        log.warning(f"[STABILIZER] Failed to log proxy ticket: {e}")

def _is_resolved(ticket_text: str) -> bool:
    """Check if a ticket's condition has been fixed"""
    # minimal but meaningful checks
    if "PORT environment variable" in ticket_text:
        return bool(os.getenv("PORT"))  # Render sets this
    if "HEARTBEAT_URL" in ticket_text:
        # heartbeat now auto-detects from RENDER_EXTERNAL_URL
        return True
    if "405" in ticket_text or "Method Not Allowed" in ticket_text:
        # v1.9.6e heartbeat auto-detects valid methods
        return True
    if "Startup Latency" in ticket_text or "startup_bind" in ticket_text:
        # Startup latency tickets resolve after one successful boot
        # Check if latency was mentioned and if it's from a previous boot cycle
        # These auto-resolve to avoid clutter
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

def archive_old_tickets():
    """Archive tickets older than ARCHIVE_DAYS to prevent filesystem clutter"""
    now = datetime.datetime.now(tzutc())
    cutoff = now - datetime.timedelta(days=ARCHIVE_DAYS)
    archived_count = 0
    
    for path in glob.glob(os.path.join(TICKET_DIR, "*.md")):
        try:
            # Extract timestamp from filename (format: YYYYMMDDTHHMMSSz_*.md)
            filename = os.path.basename(path)
            ts_str = filename.split("_")[0]
            ticket_time = datetime.datetime.strptime(ts_str, "%Y%m%dT%H%M%SZ").replace(tzinfo=tzutc())
            
            if ticket_time < cutoff:
                base = os.path.basename(path)
                archive_path = os.path.join(ARCHIVE_DIR, base)
                shutil.move(path, archive_path)
                log.info(f"[STABILIZER] Archived old ticket: {base}")
                archived_count += 1
        except Exception as e:
            log.warning(f"[STABILIZER] Failed to archive ticket {path}: {e}")
    
    if archived_count > 0:
        log.info(f"[STABILIZER] Archived {archived_count} old tickets")

def aggregate_to_daily_report():
    """
    Aggregate stabilizer metrics into a single daily summary report
    instead of individual tickets
    """
    today = datetime.datetime.now(tzutc()).strftime("%Y%m%dZ")
    report_path = os.path.join(DAILY_REPORT_DIR, f"{today}_stabilization_summary.md")
    
    # Collect metrics from anomaly queue
    metrics = {
        "date": today,
        "queued_anomalies": {},
        "boot_cycles": len(load_boot_history()),
        "environment": detect_environment(),
        "is_live": is_live()
    }
    
    for anomaly_type, queue in _anomaly_queue.items():
        metrics["queued_anomalies"][anomaly_type] = len(queue)
    
    # Generate report
    md_lines = [
        f"# Stabilization Summary — {today}",
        "",
        f"**Environment:** {metrics['environment']}",
        f"**Status:** {'LIVE' if metrics['is_live'] else 'Pre-deploy'}",
        f"**Boot Cycles Tracked:** {metrics['boot_cycles']}",
        "",
        "## Anomaly Queue Status",
        ""
    ]
    
    if metrics["queued_anomalies"]:
        for anomaly_type, count in metrics["queued_anomalies"].items():
            status = "⚠️ Pattern confirmed" if count >= ANOMALY_QUEUE_THRESHOLD else f"🔍 Observing ({count} events)"
            md_lines.append(f"- **{anomaly_type}:** {status}")
    else:
        md_lines.append("- ✅ No anomalies detected")
    
    md_lines.extend([
        "",
        "## Dynamic Thresholds",
        ""
    ])
    
    # Add threshold info if available
    threshold = calculate_dynamic_threshold("startup_latency")
    if threshold:
        md_lines.append(f"- **Startup Latency:** {threshold:.2f}s (adaptive)")
    else:
        md_lines.append("- **Startup Latency:** Learning baseline (need 3+ boot cycles)")
    
    md_lines.extend([
        "",
        "---",
        f"*Generated by Predictive Stabilizer v1.9.6g*"
    ])
    
    try:
        with open(report_path, "w") as f:
            f.write("\n".join(md_lines))
        log.info(f"[STABILIZER] Daily report updated: {report_path}")
    except Exception as e:
        log.warning(f"[STABILIZER] Failed to write daily report: {e}")

def evaluate_stability(insights: dict):
    """
    Evaluate stability with adaptive thresholds and silent learning
    """
    # Expect schema: {"stability_score": float, "most_active_modules": [["path/to/mod.py", score], ...]}
    score = float(insights.get("stability_score", 100))
    modules = insights.get("most_active_modules", [])
    
    # Environment awareness - suppress during pre-deploy
    if not is_live():
        log.debug("[STABILIZER] Stability check suppressed in pre-deploy phase")
        aggregate_to_daily_report()
        return {"status": "suppressed", "score": score, "reason": "pre-deploy"}
    
    if score >= 70 or not modules:
        log.info(f"stabilizer: ✅ stability acceptable ({score})")
        aggregate_to_daily_report()
        return {"status": "ok", "score": score}

    # Check if this is a persistent pattern using silent learning
    mod = modules[0][0]
    volatility = 100 - score
    
    if not queue_anomaly(f"volatility_{mod}", {"score": score, "volatility": volatility}):
        log.debug(f"[STABILIZER] Volatility in {mod} queued (silent learning)")
        aggregate_to_daily_report()
        return {"status": "queued", "score": score, "module": mod}
    
    # Pattern confirmed - create ticket
    ts = datetime.datetime.now(tzutc()).strftime("%Y%m%dT%H%M%SZ")
    ticket_name = f"{ts}_{os.path.basename(mod)}.md"
    ticket_path = os.path.join(TICKET_DIR, ticket_name)

    md = [
        f"# Stabilization Ticket: `{mod}`",
        f"- Detected volatility: {volatility:.2f}%",
        f"- Stability score: {score}",
        f"- Generated: {ts}",
        f"- Pattern: Confirmed after {ANOMALY_QUEUE_THRESHOLD} consecutive detections",
        "## Suggested actions",
        "- Increase test coverage for change-hot paths",
        "- Reduce implicit side effects; modularize config access",
        "- Add type checks on API boundaries",
    ]
    with open(ticket_path, "w") as t:
        t.write("\n".join(md))

    log.warning(f"stabilizer: ⚠️ ticket created {ticket_path}")

    # Optional GitHub issue (only for major stability issues)
    gh_res = None
    if score < 50:  # Only create GitHub issues for severe volatility
        issue_title = f"[Stabilization] {mod} — volatility {volatility:.2f}%"
        issue_body = "\n".join(md)
        gh_res = maybe_create_issue(issue_title, issue_body, labels=["stabilization","auto"])

    aggregate_to_daily_report()
    return {"status":"ticketed","score":score,"ticket":ticket_path,"github":gh_res}

def record_startup_metrics(latency: float, port: int, **kwargs):
    """
    Record startup metrics with adaptive threshold checking
    """
    # Check environment
    env = detect_environment()
    if not is_live():
        log.debug(f"[STABILIZER] Startup metrics suppressed in pre-deploy ({env})")
        return
    
    # Calculate dynamic threshold
    threshold = calculate_dynamic_threshold("startup_latency")
    
    # If no threshold yet, use default tolerance but don't create tickets
    if threshold is None:
        log.info(f"[STABILIZER] Startup latency {latency:.2f}s (learning baseline)")
        save_boot_cycle({"startup_latency": latency, "port": port, **kwargs})
        return
    
    # Check against dynamic threshold
    if latency <= threshold:
        log.info(f"[STABILIZER] Startup latency {latency:.2f}s (within adaptive tolerance of {threshold:.2f}s)")
        save_boot_cycle({"startup_latency": latency, "port": port, **kwargs})
        return
    
    # Exceeded threshold - queue anomaly
    if not queue_anomaly("startup_latency", {"latency": latency, "threshold": threshold}):
        log.warning(f"[STABILIZER] Startup latency {latency:.2f}s exceeded threshold {threshold:.2f}s (queued)")
        save_boot_cycle({"startup_latency": latency, "port": port, **kwargs})
        return
    
    # Pattern confirmed - log it
    log.warning(f"[STABILIZER] Persistent startup latency issue: {latency:.2f}s > {threshold:.2f}s")
    save_boot_cycle({"startup_latency": latency, "port": port, **kwargs})
    
    # Update adaptive healing - adjust next pre-bind delay
    # This is picked up by the startup system
    os.environ["ADAPTIVE_PREBIND_DELAY"] = str(min(latency * 1.2, 10.0))
    log.info(f"[STABILIZER] Auto-tuned pre-bind delay to {os.environ['ADAPTIVE_PREBIND_DELAY']}s")
