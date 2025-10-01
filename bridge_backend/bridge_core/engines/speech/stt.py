from pathlib import Path
from datetime import datetime
import uuid, json

VAULT_DIR = Path("vault/speech/stt")
VAULT_DIR.mkdir(parents=True, exist_ok=True)

def now_iso():
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"

class STTEngine:
    def __init__(self, vault=VAULT_DIR):
        self.vault = vault

    def transcribe(self, file: bytes, filename: str = "input.wav") -> dict:
        # ⚠️ Placeholder: swap with Whisper or OpenAI API later
        text = "[stub transcription]"  

        tid = str(uuid.uuid4())
        record = {
            "id": tid,
            "filename": filename,
            "created_at": now_iso(),
            "text": text
        }
        (self.vault / f"{tid}.json").write_text(json.dumps(record, indent=2))
        return record
