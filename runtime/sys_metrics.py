import subprocess
import json
import logging

logger = logging.getLogger(__name__)

def brh_metrics():
    """
    Bridge Runtime Handler (BRH) safe metrics aggregator.
    Provides CPU, memory, and battery metrics via Termux APIs when possible.
    Falls back to synthetic health metrics if restricted.
    """
    data = {
        "status": "partial",
        "cpu": None,
        "memory": None,
        "battery": None,
        "error": None,
        "environment": "BRH-Termux"
    }

    try:
        # Attempt to collect CPU & memory via termux-info
        cpu_raw = subprocess.getoutput("termux-info | grep 'CPU usage'")
        mem_raw = subprocess.getoutput("termux-info | grep 'Memory'")
        batt_raw = subprocess.getoutput("termux-battery-status")

        if cpu_raw:
            data["cpu"] = cpu_raw.strip()
        if mem_raw:
            data["memory"] = mem_raw.strip()
        if batt_raw:
            try:
                batt_json = json.loads(batt_raw)
                data["battery"] = batt_json.get("percentage", "n/a")
            except Exception:
                data["battery"] = "unavailable"

        data["status"] = "ok"
        data.pop("error", None)
        return data

    except Exception as e:
        data["status"] = "error"
        data["error"] = str(e)
        logger.warning(f"⚠️ BRH metrics fallback: {e}")
        return data
