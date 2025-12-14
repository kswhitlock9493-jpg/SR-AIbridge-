import yaml
import os
import json
import hashlib


def gather_meta():
    """Gather all YAML/YML files from the repository."""
    meta = {}
    for root, _, files in os.walk("."):
        # Skip .git and node_modules directories
        if ".git" in root or "node_modules" in root:
            continue
        for f in files:
            if f.endswith((".yaml", ".yml")):
                filepath = os.path.join(root, f)
                try:
                    with open(filepath, encoding="utf-8") as fp:
                        data = yaml.safe_load(fp)
                        meta[filepath] = data
                except (yaml.YAMLError, OSError, IOError):
                    # Skip files that can't be parsed or read
                    pass
    return meta


def validate_facts(meta):
    """Validate and deduplicate facts from metadata."""
    truth = {}
    for name, data in meta.items():
        if not isinstance(data, dict):
            continue
        for k, v in data.items():
            # Convert value to string for hashing
            val_str = json.dumps(v) if isinstance(v, (dict, list)) else str(v)
            sig = hashlib.sha256(f"{k}:{val_str}".encode()).hexdigest()[:12]
            truth[sig] = {"key": k, "value": v, "source": name}
    return truth
