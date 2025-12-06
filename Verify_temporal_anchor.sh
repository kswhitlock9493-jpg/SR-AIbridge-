
---

### 2.  `verify_temporal_anchor.sh`  (executable, peer-friendly)

```bash
#!/usr/bin/env bash
# Dominion Temporal Anchor – Peer Verification Script
# Run: chmod +x verify_temporal_anchor.sh && ./verify_temporal_anchor.sh

set -euo pipefail

PDFS=("URT_Playbook.pdf" "Resonance_Radar_Design.pdf" "Whitlock_Coefficient_Analysis.pdf" "Bridge_Implementation_Guide.pdf")
ANCHOR_FILE="TEMPORAL_ANCHOR.md"

# 1.  Files exist?
for pdf in "${PDFS[@]}"; do
    [[ -f $pdf ]] || { echo "❌ Missing $pdf"; exit 1; }
done
[[ -f $ANCHOR_FILE ]] || { echo "❌ Missing $ANCHOR_FILE"; exit 1; }

# 2.  Compute live Merkle root
LIVE_ROOT=$(sha256sum "${PDFS[@]}" | sha256sum | awk '{print $1}')

# 3.  Extract stamped root
STAMPED_ROOT=$(grep -m1 '^Root:' "$ANCHOR_FILE" | awk '{print $2}')

# 4.  Match?
if [[ "$LIVE_ROOT" == "$STAMPED_ROOT" ]]; then
    echo "✅ Merkle root verified: $LIVE_ROOT"
else
    echo "❌ Merkle mismatch!"
    echo "  Live:   $LIVE_ROOT"
    echo "  Stamped:$STAMPED_ROOT"
    exit 1
fi

# 5.  Commit hash
LIVE_COMMIT=$(git rev-parse HEAD)
STAMPED_COMMIT=$(grep -m1 '^Commit hash:' "$ANCHOR_FILE" | awk '{print $3}')
if [[ "$LIVE_COMMIT" == "$STAMPED_COMMIT" ]]; then
    echo "✅ Commit hash verified: $LIVE_COMMIT"
else
    echo "❌ Commit hash mismatch!"
    exit 1
fi

# 6.  Date (within 5 min tolerance)
LIVE_DATE=$(date -u +%s)
STAMPED_DATE=$(date -d "$(grep -m1 '^Date:' "$ANCHOR_FILE" | awk '{print $2}')" +%s)
DELTA=$((LIVE_DATE - STAMPED_DATE))
if (( DELTA <= 300 && DELTA >= -300 )); then
    echo "✅ Date verified (±5 min): $(date -u -d @$STAMPED_DATE +'%Y-%m-%dT%H:%M:%SZ')"
else
    echo "❌ Date outside tolerance (±5 min)"
    exit 1
fi

echo "🜂 Temporal Anchor is valid – harmonic integrity locked."
