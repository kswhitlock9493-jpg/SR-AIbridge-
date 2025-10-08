# Bridge Parity Engine with Triage (v1.6.9)
Automated wiring and health audit between backend and frontend.

## Modes
- Local Run: `python3 bridge_backend/tools/parity_engine.py`
- CI Auto-Run: GitHub workflow `bridge_parity_check.yml`

## Triage Levels
- Critical → Missing active endpoint used by client.
- Moderate → Extra or deprecated route.
- Informational → Diagnostics/health endpoint desync.

## Output
`bridge_backend/diagnostics/bridge_parity_report.json` contains counts + severity.

See example report: `bridge_backend/diagnostics/bridge_parity_report_example.json`

## Benefits
✅ Continuous route integrity verification  
✅ Immediate triage for mismatches  
✅ Zero-manual backend/frontend alignment
