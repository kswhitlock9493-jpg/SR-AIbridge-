from typing import Dict, List
from .types import DiffEntry

def compute_diff(canonical: Dict[str,str], remote: Dict[str,str], allow_deletions: bool) -> List[DiffEntry]:
    diff: List[DiffEntry] = []
    # create/update
    for k, v in canonical.items():
        if k not in remote:
            diff.append({"key": k, "op": "create", "from_val": None, "to_val": v})
        elif remote[k] != v:
            diff.append({"key": k, "op": "update", "from_val": remote[k], "to_val": v})
        else:
            diff.append({"key": k, "op": "noop", "from_val": v, "to_val": v})
    # delete (optional)
    if allow_deletions:
        for k in remote.keys() - canonical.keys():
            diff.append({"key": k, "op": "delete", "from_val": remote[k], "to_val": None})
    return diff
