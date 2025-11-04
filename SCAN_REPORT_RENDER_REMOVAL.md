# Repository Scan Report - Render Removal Readiness

**Date:** Tue Nov  4 02:30:49 UTC 2025

## Summary

- Issues: 3
- Info: 13
- Render References: 36 files
- BRH References: 28 files
- Forge References: 33 files

## Issues

- ❌ Token Forge Dominion module not found
- ❌ .env.example still references Render
- ❌ Frontend config.js still defaults to Render

## Information

- ✅ Backend main.py has Forge references
- ✅ Forge engine directory exists: /home/runner/work/SR-AIbridge-/SR-AIbridge-/bridge_backend/forge
- ✅ BRH directory exists
-   ✅ BRH run.py exists
-   ✅ BRH api.py exists
-   ✅ BRH forge_auth.py exists
-   ✅ BRH README.md exists
- ✅ bridge.runtime.yaml exists
- ⚠️  render.yaml still exists (can be removed)
- ⚠️  Render script exists: render_collect.py
- ⚠️  Render script exists: render_env_lint.py
- ⚠️  Render script exists: runtime_triage_render.py
- ⚠️  2 Render-related workflow(s) found

## Render References by File

### bridge-frontend/netlify/functions/health.ts

- Line 15: `const backend = process.env.RENDER_HEALTH_URL || "https://sr-aibridge.onrender.com/api/health";`

### bridge-frontend/src/config.js

- Line 2: `export const API_BASE = import.meta.env.VITE_API_BASE || "https://sr-aibridge.onrender.com";`
- Line 15: `: "wss://sr-aibridge.onrender.com")`

### bridge_backend/bridge_core/engines/envsync/providers/render.py

- Line 23: `url = f"https://api.render.com/v1/services/{self.service_id}/env-vars"`
- Line 37: `url = f"https://api.render.com/v1/services/{self.service_id}/env-vars"`

### bridge_backend/config.py

- Line 77: `"https://*.onrender.com",  # All Render subdomains`

### bridge_backend/diagnostics/full_scan_report.json

- Line 345: `"BRIDGE_API_URL": "https://sr-aibridge.onrender.com",`
- Line 347: `"VITE_API_BASE": "https://sr-aibridge.onrender.com",`
- Line 348: `"REACT_APP_API_URL": "https://sr-aibridge.onrender.com",`
- Line 358: `"VITE_API_BASE": "https://sr-aibridge.onrender.com",`
- Line 359: `"REACT_APP_API_URL": "https://sr-aibridge.onrender.com",`
- Line 364: `"BRIDGE_API_URL": "https://sr-aibridge.onrender.com",`

### bridge_backend/engines/envrecon/core.py

- Line 37: `url = f"https://api.render.com/v1/services/{service_id}/env-vars"`

### bridge_backend/engines/hydra/guard.py

- Line 47: `return """/api/*   https://sr-aibridge.onrender.com/:splat   200`

### bridge_backend/engines/steward/adapters/render_adapter.py

- Line 12: `"""Adapter for Render.com environment variables"""`

### bridge_backend/main.py

- Line 91: `"https://sr-aibridge.netlify.app,https://sr-aibridge.onrender.com"`

### bridge_backend/middleware/headers.py

- Line 40: `"https://sr-aibridge.netlify.app,https://sr-aibridge.onrender.com"`

### bridge_backend/runtime/egress_canary.py

- Line 16: `"api.render.com",`
- Line 17: `"render.com",`

### bridge_backend/runtime/heartbeat.py

- Line 27: `return "https://sr-aibridge.onrender.com/health"`

### bridge_backend/runtime/parity.py

- Line 45: `"https://sr-aibridge.onrender.com"`

### bridge_backend/scripts/api_triage.py

- Line 34: `BASE_URL = os.getenv("BRIDGE_BASE_URL", "https://sr-aibridge.onrender.com")`

### bridge_backend/scripts/deploy_diagnose.py

- Line 20: `url = f"https://api.render.com/v1/services/{RENDER_SERVICE_ID}/deploys"`

### bridge_backend/scripts/endpoint_triage.py

- Line 22: `BASE_URL = os.getenv("BRIDGE_BASE_URL", "https://sr-aibridge.onrender.com")`

### bridge_backend/scripts/env_sync_monitor.py

- Line 12: `RENDER = os.getenv("RENDER_HEALTH_URL", "https://sr-aibridge.onrender.com/api/health")`

### bridge_backend/scripts/generate_sync_badge.py

- Line 32: `"https://sr-aibridge.onrender.com/api/health",`

### bridge_backend/scripts/hooks_triage.py

- Line 20: `BASE_URL = os.getenv("BRIDGE_BASE_URL", "https://sr-aibridge.onrender.com")`

### bridge_backend/tests/test_runtime_guards.py

- Line 42: `"api.render.com",`

### bridge_backend/tests/test_total_stack_triage.py

- Line 224: `assert "api.render.com" in code`

### bridge_backend/tools/firewall_intel/analyze_firewall_findings.py

- Line 53: `"api.render.com",`
- Line 54: `"render.com",`

### bridge_backend/tools/firewall_intel/fetch_firewall_incidents.py

- Line 98: `response = requests.get("https://api.render.com/", timeout=10)`

### bridge_backend/tools/network_diagnostics/check_copilot_access.py

- Line 22: `"https://api.render.com",`
- Line 25: `"https://sr-aibridge.onrender.com/api",`

### bridge_backend/tools/parity_engine.py

- Line 90: `prefix="https://sr-aibridge.onrender.com"`

### netlify.toml

- Line 18: `to = "https://sr-aibridge.onrender.com/:splat"`

### render.yaml

- Line 26: `value: postgresql://sr_admin:<YOUR_PASSWORD>@dpg-d3i3jc0dl3ps73csp9e0-a.oregon-postgres.render.com/s`
- Line 28: `value: https://sr-aibridge.onrender.com`
- Line 44: `value: https://bridge.netlify.app,https://sr-aibridge.netlify.app,https://sr-aibridge.onrender.com`

### scripts/check_env_parity.py

- Line 17: `url = f"https://api.render.com/v1/services/{service_id}/env-vars"`

### scripts/firewall_watchdog.py

- Line 21: `BRIDGE_URL = os.getenv("BRIDGE_URL", "https://sr-aibridge.onrender.com")`
- Line 26: `"sr-aibridge.onrender.com",`
- Line 126: `"render.com",`

### scripts/integrity_audit.py

- Line 17: `"Render": "https://sr-aibridge.onrender.com/health",`

### scripts/repair_netlify_env.py

- Line 9: `"VITE_API_BASE": "https://sr-aibridge.onrender.com/api",`
- Line 10: `"REACT_APP_API_URL": "https://sr-aibridge.onrender.com/api",`

### scripts/synthesize_netlify_artifacts.py

- Line 34: `redirects.write_text("""/api/* https://sr-aibridge.onrender.com/:splat 200!`

### scripts/validate_copilot_env.py

- Line 14: `"https://render.com",`

### test_endpoints_full.py

- Line 398: `%(prog)s https://your-backend.onrender.com # Test deployed backend`

### tests/test_anchorhold_protocol.py

- Line 79: `assert "https://sr-aibridge.onrender.com" in content`
- Line 146: `assert "https://sr-aibridge.onrender.com" in content`

### tests/test_v196g_features.py

- Line 25: `with patch.dict(os.environ, {"RENDER_EXTERNAL_URL": "https://test.onrender.com"}):`
- Line 56: `with patch.dict(os.environ, {"RENDER_EXTERNAL_URL": "https://test.onrender.com", "PORT": "10000"}):`
- Line 62: `with patch.dict(os.environ, {"RENDER_EXTERNAL_URL": "https://test.onrender.com"}, clear=True):`
- Line 235: `with patch.dict(os.environ, {"RENDER_EXTERNAL_URL": "https://test.onrender.com"}, clear=True):`

