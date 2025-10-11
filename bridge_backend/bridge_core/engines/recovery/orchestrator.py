from pathlib import Path
from datetime import datetime, timezone
import uuid, json

try:
    from bridge_core.engines.autonomy.service import AutonomyEngine
    from bridge_core.engines.parser.service import ParserEngine
except ImportError:
    from bridge_backend.bridge_core.engines.autonomy.service import AutonomyEngine
    from bridge_backend.bridge_core.engines.parser.service import ParserEngine

VAULT = Path("vault/recovery")
VAULT.mkdir(parents=True, exist_ok=True)

class RecoveryOrchestrator:
    def __init__(self):
        self.autonomy = AutonomyEngine()
        self.parser = ParserEngine()

    def _vault_log(self, obj: dict, kind: str):
        stamp = datetime.now(timezone.utc).isoformat() + "Z"
        obj["timestamp"] = stamp
        obj["kind"] = kind
        fid = f"{kind}_{uuid.uuid4().hex}.json"
        (VAULT / fid).write_text(json.dumps(obj, indent=2))
        return obj

    def dispatch_and_ingest(self, project: str, captain: str, permissions: dict, objective: str, raw: str):
        # Step 1: Create task
        task = self.autonomy.create_task(project, captain, objective, permissions, "hybrid")
        task_dict = task.__dict__ if hasattr(task, '__dict__') else task
        self._vault_log(task_dict, "task_created")

        # Step 2: File raw text via parser
        manifest = self.parser.ingest(raw, source=f"task:{task_dict['id']}")
        manifest_dict = manifest.__dict__ if hasattr(manifest, '__dict__') else manifest
        self._vault_log(manifest_dict, "parsed_manifest")

        # Step 3: Link task → manifest
        linkage = {"task_id": task_dict["id"], "manifest": manifest_dict}
        self._vault_log(linkage, "linkage")

        return {"task": task_dict, "manifest": manifest_dict, "linkage": linkage}