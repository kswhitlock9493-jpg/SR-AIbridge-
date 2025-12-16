# Triage System Architecture

SR-AIbridge has two triage systems that serve different purposes:

## 1. Legacy Triage Scripts (`bridge_backend/scripts/`)

**Location:** `bridge_backend/scripts/api_triage.py`, `endpoint_triage.py`, `hooks_triage.py`

**Purpose:**
- Standalone triage scripts with detailed schema validation
- Run on backend startup (via `main.py`)
- Individual GitHub Actions workflows (api-triage.yml, endpoint-triage.yml, hooks-triage.yml)
- Generate detailed reports with notifications to Bridge diagnostics endpoint

**Features:**
- Schema validation for API responses
- Direct notification to Bridge frontend
- Detailed error reporting
- Manual/automatic modes

## 2. Federation Triage System (`bridge_backend/tools/triage/`)

**Location:** `bridge_backend/tools/triage/{api,endpoint,diagnostics_federate}.py`

**Purpose:**
- Unified federation-based triage with retry/backoff logic
- Used by `triage_federation.yml` workflow
- Lighter-weight health checks focused on federation
- Aggregates multiple triage reports into one federation report

**Features:**
- Exponential backoff and jitter for retry logic
- Circuit breaker pattern
- Parity-aware endpoint testing
- Federation heartbeat aggregation
- Auto-healing capabilities

## Why Both Exist

The federation system (tools/triage) is newer and more robust, but the legacy system (scripts/) is still actively used for:
1. Backend startup health checks
2. Detailed schema validation
3. Individual endpoint monitoring
4. Direct frontend notifications

Both systems are maintained and serve complementary roles in the overall health monitoring strategy.
