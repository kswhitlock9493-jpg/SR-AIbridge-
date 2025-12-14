from typing import Dict, List, Optional, Literal, TypedDict

Mode = Literal["dry-run", "enforce"]

class ProviderVars(TypedDict):
    provider: str
    items: Dict[str, str]

DiffOp = Literal["create","update","delete","noop"]

class DiffEntry(TypedDict):
    key: str
    op: DiffOp
    from_val: Optional[str]
    to_val: Optional[str]

class SyncResult(TypedDict):
    provider: str
    mode: Mode
    applied: bool
    diff: List[DiffEntry]
    errors: List[str]
