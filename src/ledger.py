Append-only cryptographic custody ledger.
Each entry stores prev_hash/self_hash for full chain integrity.
import os, json, time, hashlib, base64
from typing import Optional, Dict, Any, List
from pathlib import Path
from nacl.signing import SigningKey
LEDGER_PATH = "vault/custody.scroll"
os.makedirs(os.path.dirname(LEDGER_PATH), exist_ok=True)

def atomic_append_jsonl(path: str, obj: Dict[str, Any]) -> None:
    line = json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + "\n"
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
    try:
        os.write(fd, line.encode("utf-8")); os.fsync(fd)
    finally: os.close(fd)

def sha256_bytes(b: bytes) -> str: return hashlib.sha256(b).hexdigest()

class Ledger:
    def __init__(self, path: str = LEDGER_PATH):
        self.path = path; Path(path).parent.mkdir(parents=True, exist_ok=True)
    def _last_hash(self) -> Optional[str]:
        if not os.path.exists(self.path): return None
        last=None
        with open(self.path,"rb") as f:
            for line in f: last=line
        if not last: return None
        return json.loads(last.decode("utf-8")).get("_self_hash")
    def append(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        prev=self._last_hash(); ts=time.time()
        payload={"timestamp":ts,"payload":entry,"prev_hash":prev}
        b=json.dumps(payload,sort_keys=True,separators=(",",":")).encode()
        payload["_self_hash"]=sha256_bytes(b)
        atomic_append_jsonl(self.path,payload); return payload
    def iter_entries(self)->List[Dict[str,Any]]:
        if not os.path.exists(self.path): return []
        return [json.loads(l) for l in open(self.path,"r",encoding="utf-8")]
    def verify_chain(self)->bool:
        prev=None
        for e in self.iter_entries():
            if e.get("prev_hash")!=prev: return False
            copy={k:e[k] for k in e if k!="_self_hash"}
            b=json.dumps(copy,sort_keys=True,separators=(",",":")).encode()
            if sha256_bytes(b)!=e.get("_self_hash"): return False
            prev=e.get("_self_hash")
        return True
    def export_signed_snapshot(self,out:str,sk_hex:Optional[str]=None)->str:
        entries=self.iter_entries()
        snap={"created_at":time.time(),"entries":entries}
        Path(out).parent.mkdir(parents=True,exist_ok=True)
        with open(out,"w",encoding="utf-8") as f: json.dump(snap,f,indent=2)
        data=json.dumps(snap,sort_keys=True,separators=(",",":")).encode()
        sk=SigningKey(bytes.fromhex(sk_hex)) if sk_hex else SigningKey.generate()
        sig=sk.sign(data).signature; sig_b64=base64.b64encode(sig).decode()
        sig_path=out+".sig"
        with open(sig_path,"w") as f: json.dump({"signature_b64":sig_b64,"pub_hex":sk.verify_key.encode().hex()},f)
        return sig_path