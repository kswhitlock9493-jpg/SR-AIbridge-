import time
import logging

def safe_autoheal_init(link_bus_callable, retries: int = 5, backoff: float = 1.5) -> bool:
    """
    Attempts to link Umbra Auto-Heal to Genesis bus with bounded backoff.
    """
    for i in range(retries):
        try:
            link_bus_callable()  # must raise on failure
            logging.info("🩺 Umbra Auto-Heal: linked to Genesis bus.")
            return True
        except Exception as e:
            logging.warning(f"Umbra Auto-Heal retry {i+1}/{retries}: {e}")
            time.sleep(backoff)
    logging.error("💔 Umbra Auto-Heal: exhausted retries.")
    return False
