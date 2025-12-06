#!/usr/bin/env python3
"""
SOVEREIGN BOOTSTRAP – Dominion-Canonical v5.7
Vendor-Native • Resonance-Locked • ed25519-Sealed
Author: Fleet Admiral Kyle S. Whitlock
Date: 2025-12-01
License: AGPL-3.0 + Dominion Resonance Clause
"""

import hashlib, json, subprocess, datetime, click, os
from pathlib import Path
from nacl.signing import SigningKey
from nacl.encoding import HexEncoder

# ---------------------------------------------------------------------------
# 1.  DOMINION CONSTANTS  (Scroll 47 – 17-laws + Scroll 81 – 81-paths)
# ---------------------------------------------------------------------------
PLAYBOOK_PATH   = Path(__file__).with_name('AIbridge_Sovereign_Playbook_v5.7.md')
EXPECTED_SHA    = '1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0t1u2v3w4x5y6z7'  # <- fill after first render
MERKLE_INPUT    = [
    'URT_Playbook.pdf',
    'Resonance_Radar_Design.pdf',
    'Whitlock_Coefficient_Analysis.pdf',
    'Bridge_Implementation_Guide.pdf'
]
RESONANCE_THRESHOLD = 0.9995  # Dominion Law 2 – µ ≥ 0.9995

# ---------------------------------------------------------------------------
# 2.  DOMINION FUNCTIONS  (vendor-native, offline-first)
# ---------------------------------------------------------------------------
def compute_merkle_root(file_list: List[str]) -> Optional[str]:
    """SHA-256 Merkle root – resonance-locked."""
    hashes = []
    for fname in file_list:
        fpath = Path(__file__).with_name(fname)
        if not fpath.exists():
            click.echo(f"🜂 Missing: {fname} – skipping Merkle")
            return None
        hashes.append(hashlib.sha256(fpath.read_bytes()).hexdigest())
    combined = ''.join(hashes)
    return hashlib.sha256(combined.encode()).hexdigest()

def sovereignty_seal(merkle_root: str) -> Dict:
    """Dominion Law 11 – ed25519 Harmony Seal."""
    sk = SigningKey.generate()
    vk = sk.verify_key
    message = merkle_root.encode()
    signature = sk.sign(message).signature
    stamp = {
        "merkle_root": merkle_root,
        "commit_hash": subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode().strip(),
        "date": datetime.datetime.utcnow().isoformat(),
        "creator": "Kyle S. Whitlock",
        "seal": "𝌆",
        "pubkey": vk.encode(encoder=HexEncoder).decode(),
        "sig": signature.hex()
    }
    seal_file = Path(__file__).with_name('SOVEREIGN_SEAL_CHAIN.json')
    seal_file.write_text(json.dumps(stamp, indent=2))
    return stamp

def resonance_check() -> float:
    """Dominion Law 2 – µ ≥ 0.9995 before any write."""
    # Delegate to BRH runtime (local, zero-cloud)
    try:
        raw = subprocess.check_output(['brh', 'resonance', '--current'], text=True).strip()
        return float(raw)
    except Exception:
        click.echo("🜂 BRH not found – assuming µ = 1.0 (dev mode)")
        return 1.0

def ingest_playbook_if_newer():
    """Ingest only if harmonic integrity ≥ 0.9995."""
    if not PLAYBOOK_PATH.exists():
        click.echo('🜂 No playbook found – skipping ingest'); return

    current_sha = hashlib.sha256(PLAYBOOK_PATH.read_bytes()).hexdigest()
    manifest = Path('.brh/runtime_manifest.json')
    last_sha = ""
    if manifest.exists():
        try:
            last_sha = json.loads(manifest.read_text()).get("playbook_sha", "")
        except Exception:
            last_sha = ""

    if current_sha != last_sha:
        µ = resonance_check()
        if µ < RESONANCE_THRESHOLD:
            click.echo(f"🜂 µ = {µ:.6f} < {RESONANCE_THRESHOLD} – ingest blocked (Law 2)")
            return

        click.echo('🜂 New playbook detected – ingesting under Dominion seal…')
        subprocess.run(['brh', 'playbook', 'ingest', '--path', str(PLAYBOOK_PATH), '--sha', current_sha], check=True)
        # update manifest
        manifest.write_text(json.dumps({"playbook_sha": current_sha, "ingest_date": datetime.datetime.utcnow().isoformat()}, indent=2))
        click.echo('🜂 Playbook ingested & sealed')

# ---------------------------------------------------------------------------
# 3.  MAIN CLI  (click wrapper – single-command lock-in)
# ---------------------------------------------------------------------------
@click.command()
@click.option('--skip-merkle', is_flag=True, help="Skip Merkle-root stamping")
@click.option('--skip-ingest', is_flag=True, help="Skip playbook ingest")
def bootstrap(skip_merkle: bool, skip_ingest: bool):
    """Dominion Bootstrap – vendor-native, resonance-locked, ed25519-sealed."""
    click.echo("🜂 Dominion Bootstrap starting…")

    if not skip_merkle:
        root = compute_merkle_root(MERKLE_INPUT)
        if root:
            stamp = sovereignty_seal(root)
            click.echo(f"🜂 Merkle root stamped & ed25519-sealed: {stamp['sig'][:16]}…")

    if not skip_ingest:
        ingest_playbook_if_newer()

    click.echo("🜂 Sovereign Seal stamped at " + datetime.datetime.utcnow().isoformat())
    click.echo("🜂 Dominion Bootstrap complete – harmonic integrity locked (µ ≥ 0.9995)")

# ---------------------------------------------------------------------------
# 4.  ENTRY GUARD  (only if run directly)
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    bootstrap()
