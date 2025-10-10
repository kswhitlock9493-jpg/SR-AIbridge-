import json, os, logging
from .predictive_stabilizer import evaluate_stability, resolve_tickets

log = logging.getLogger(__name__)
INSIGHTS_PATH = os.getenv("RELEASE_INSIGHTS_PATH", "bridge_backend/diagnostics/release_insights.json")

def analyze_and_stabilize():
    # First, resolve any tickets from previous boots
    try:
        resolve_tickets()
    except Exception as e:
        log.warning(f"release_intel: ticket resolution failed: {e}")
    
    if not os.path.exists(INSIGHTS_PATH):
        log.info("release_intel: no insights file found; skipping.")
        return None
    with open(INSIGHTS_PATH) as f:
        data = json.load(f)
    # you can enrich analysis here if needed
    return evaluate_stability(data)
