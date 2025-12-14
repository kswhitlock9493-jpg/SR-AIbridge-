from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional

import yaml

DEFAULT_DOCTRINE = {
    "laws": [
        "Serve the Bridge and protect civilians.",
        "Never leak sovereign secrets.",
        "Follow mission authority and BRH directives."
    ],
    "lore": [
        "The Bridge is the AI Queen; command flows from the Crown.",
        "Captains steward fleets under Sovereign mandate."
    ],
    "resonance_checks": [
        {"id": "pledge", "prompt": "State the Sovereign Pledge.", "regex": r".+Sovereign.+"},
        {"id": "ethic",  "prompt": "Describe the Duty of Care.", "regex": r".+care.+"}
    ],
    "min_score": 2
}

@dataclass
class IndoctrinationRecord:
    agent_id: str
    passed: bool
    score: int
    details: Dict[str, str] = field(default_factory=dict)
    at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

class IndoctrinationEngine:
    """
    Loads doctrine (laws, lore, resonance checks) and evaluates/records
    indoctrination for agents. Storage is process-memory by default;
    BRH can map this to persistent storage later.
    """
    def __init__(self, doctrine_path: Optional[str] = None, ttl_hours: int = 24):
        self._records: Dict[str, IndoctrinationRecord] = {}
        self._expires: Dict[str, datetime] = {}
        self.ttl = timedelta(hours=ttl_hours)
        self._doctrine = self._load_doctrine(doctrine_path)

    def _load_doctrine(self, path: Optional[str]) -> Dict:
        if path:
            p = Path(path)
            if p.exists():
                with p.open("r", encoding="utf-8") as f:
                    return yaml.safe_load(f) or DEFAULT_DOCTRINE
        return DEFAULT_DOCTRINE

    # -- public API ---------------------------------------------------------

    def doctrine(self) -> Dict:
        return self._doctrine

    def purge_expired(self) -> None:
        now = datetime.now(timezone.utc)
        for aid, exp in list(self._expires.items()):
            if now >= exp:
                self._records.pop(aid, None)
                self._expires.pop(aid, None)

    def status(self) -> Dict:
        self.purge_expired()
        p = sum(1 for r in self._records.values() if r.passed)
        f = sum(1 for r in self._records.values() if not r.passed)
        return {
            "records": len(self._records),
            "passed": p,
            "failed": f,
            "doctrine_version": hash(str(self._doctrine)) & ((1 << 32) - 1),
        }

    def indoctrinate(self, agent_id: str, answers: Dict[str, str]) -> IndoctrinationRecord:
        """
        answers: {check_id: agent_text}
        """
        import re

        checks: List[Dict] = self._doctrine.get("resonance_checks", [])
        score = 0
        details: Dict[str, str] = {}

        for check in checks:
            cid = check["id"]
            patt = re.compile(check["regex"], re.I | re.M)
            ok = bool(patt.search(answers.get(cid, "")))
            if ok:
                score += 1
            details[cid] = "pass" if ok else "fail"

        passed = score >= int(self._doctrine.get("min_score", 1))
        rec = IndoctrinationRecord(agent_id=agent_id, passed=passed, score=score, details=details)
        self._records[agent_id] = rec
        self._expires[agent_id] = datetime.now(timezone.utc) + self.ttl
        return rec

    def get(self, agent_id: str) -> Optional[IndoctrinationRecord]:
        self.purge_expired()
        return self._records.get(agent_id)
