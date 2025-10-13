import os
import time
import logging

def delayed_integrity_check(run_integrity_callable):
    """
    Sleep briefly so Reflex/Umbra/Genesis finish bootstrapping, then run integrity.
    """
    # Read the delay value at call time to allow for runtime configuration
    delay_sec = float(os.getenv("INTEGRITY_DEFER_SECONDS", "3"))
    logging.info(f"🧪 Integrity: deferring integrity check for {delay_sec:.1f}s…")
    time.sleep(delay_sec)
    return run_integrity_callable()
