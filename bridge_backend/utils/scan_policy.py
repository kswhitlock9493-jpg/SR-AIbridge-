import yaml
from pathlib import Path
from typing import Dict, Any

DEFAULT = {
  "blocked_licenses": ["GPL-2.0","GPL-3.0","AGPL-3.0"],
  "allowed_licenses": ["MIT","Apache-2.0","BSD-3-Clause"],
  "thresholds": {"counterfeit_confidence_block": 0.94, "counterfeit_confidence_flag": 0.6},
  "max_file_size_bytes": 750_000,
  "scan_exclude_paths": ["node_modules",".venv","__pycache__","bridge_backend/scan_reports"]
}

def load_policy(path: str="scan_policy.yaml") -> Dict[str, Any]:
    p = Path(path)
    if not p.exists():
        return DEFAULT
    return {**DEFAULT, **yaml.safe_load(p.read_text())}
