# Recovery Orchestrator — Doctrine (v1)

## Purpose:
- Fuse autonomy (action) and parsing (memory).
- Ensure every agent action yields recoverable knowledge.

## Rituals:
- Every dispatch → sealed task in vault.
- Every raw → parsed chunks → filed manifest.
- Every linkage → recorded, so provenance chains are never broken.

## Laws:
- Nothing unfiled. If autonomy acts, parser seals.
- No orphan results. Every manifest must tie back to its originating task.
- Recovery is recursive: outputs can feed back into new tasks.

## Implementation Notes:
- Uses hybrid mode for autonomy tasks to enable both screen and connector capabilities
- All operations are logged to `vault/recovery/` with UUID-based filenames
- Maintains bidirectional linkage between tasks and their parser manifests
- Provides atomic dispatch-and-ingest operations via single API endpoint