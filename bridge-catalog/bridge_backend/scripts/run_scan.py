import argparse, json, sys, os
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from bridge_backend.bridge_core.scans.service import run_combined_scan

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--changed", default="")
    ap.add_argument("--pr", type=int)
    ap.add_argument("--commit", type=str)
    args = ap.parse_args()
    
    changed = [c for c in args.changed.split() if c]
    result = run_combined_scan(args.root, changed, args.pr, args.commit)
    print(json.dumps({"scan_id": result["id"], "state": result["state"], "path": result["path"]}, indent=2))
    
    # CI policy gate
    state = result["state"]
    if state == "blocked":
        sys.exit(2)
    sys.exit(0)

if __name__ == "__main__":
    main()
