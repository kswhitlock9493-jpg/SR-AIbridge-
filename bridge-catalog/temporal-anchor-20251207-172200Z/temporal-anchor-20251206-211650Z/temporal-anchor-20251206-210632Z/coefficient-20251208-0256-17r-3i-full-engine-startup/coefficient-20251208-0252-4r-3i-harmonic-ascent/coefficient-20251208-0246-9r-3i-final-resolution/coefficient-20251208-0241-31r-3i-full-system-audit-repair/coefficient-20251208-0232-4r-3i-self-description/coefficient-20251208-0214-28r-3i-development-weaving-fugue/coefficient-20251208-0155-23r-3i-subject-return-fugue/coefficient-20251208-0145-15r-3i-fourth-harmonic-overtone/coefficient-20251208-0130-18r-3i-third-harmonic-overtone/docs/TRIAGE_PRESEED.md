# Triage Pre-Seed System - Operation Genesis

## Overview

The Triage Pre-Seed system ensures that the Bridge dashboard and Unified Health Timeline display meaningful data immediately after deployment by seeding all diagnostic and triage systems with initial baseline data.

## Architecture

### Components

1. **Pre-Seed Script** (`bridge_backend/scripts/triage_preseed.py`)
   - Generates baseline reports for all triage systems
   - Creates unified timeline with baseline events
   - Runs automatically on backend startup

2. **Utility Functions** (`bridge_backend/scripts/utils.py`)
   - Provides `now()` function for consistent ISO 8601 timestamps
   - Shared by all triage scripts

3. **Startup Integration** (`bridge_backend/main.py`)
   - Runs pre-seed before other triage systems
   - Ensures baseline data exists from first boot

4. **GitHub Workflow** (`.github/workflows/triage-preseed.yml`)
   - Manual workflow dispatch for re-seeding
   - Uploads baseline to Bridge diagnostics endpoint
   - Creates artifacts for verification

5. **Frontend Banner** (`bridge-frontend/src/components/TriageBootstrapBanner.jsx`)
   - Shows confirmation when all triage systems are seeded
   - Auto-hides when seeding is incomplete
   - Displays in green banner with checkmark

## Event Flow

```
1. Backend Startup
   Backend Starts → Pre-Seed Script Runs
        ↓
   Generate Baseline Reports:
   - ci_cd_report.json (HEALTHY)
   - endpoint_report.json (HEALTHY)
   - api_triage_report.json (HEALTHY)
   - hooks_triage_report.json (HEALTHY)
        ↓
   Build unified_timeline.json with all baseline events
        ↓
   Run normal triage scripts (they can overwrite seeded data)
        ↓
   Frontend fetches /api/diagnostics/timeline/unified
        ↓
   TriageBootstrapBanner shows if all 4 triage types exist

2. Manual Workflow Trigger
   GitHub Actions Manual Trigger
        ↓
   Run triage_preseed.py
        ↓
   Upload unified_timeline.json to Bridge
        ↓
   Save artifacts for review
```

## Files Created/Modified

### Created Files
- `bridge_backend/scripts/utils.py` - Timestamp utility
- `bridge_backend/scripts/triage_preseed.py` - Pre-seed generator
- `.github/workflows/triage-preseed.yml` - Manual workflow
- `bridge-frontend/src/components/TriageBootstrapBanner.jsx` - Status banner

### Modified Files
- `bridge_backend/main.py` - Added pre-seed to startup sequence
- `bridge_backend/.gitignore` - Added hooks_triage_report.json

## Usage

### Automatic Execution

The pre-seed runs automatically:
1. **On Backend Startup**: Immediately after server initialization, before other triage runs
2. **Via Manual Workflow**: Trigger from GitHub Actions UI

### Manual Execution

```bash
cd bridge_backend
python3 scripts/triage_preseed.py
```

This will:
1. Create all 4 baseline triage reports
2. Build unified timeline with baseline events
3. Display confirmation messages

### Frontend Integration

Add the TriageBootstrapBanner to any page that shows diagnostic information:

```jsx
import TriageBootstrapBanner from './components/TriageBootstrapBanner';

function DiagnosticsPage() {
  return (
    <div>
      <TriageBootstrapBanner />
      {/* Other diagnostic components */}
    </div>
  );
}
```

The banner will:
- Fetch `/api/diagnostics/timeline/unified`
- Check for all 4 triage types (CI_CD_TRIAGE, ENDPOINT_TRIAGE, API_TRIAGE, HOOKS_TRIAGE)
- Display green banner if all are present
- Hide itself if any are missing

## Baseline Report Structure

Each seeded report follows this structure:

```json
{
  "type": "ENDPOINT_TRIAGE",
  "status": "HEALTHY",
  "source": "PreSeed",
  "meta": {
    "timestamp": "2025-10-07T14:20:45.840129+00:00",
    "note": "Baseline initialization seed",
    "results": [],
    "environment": "backend"
  }
}
```

The unified timeline is an array of these reports, sorted by timestamp.

## Integration with Existing Systems

The pre-seed system integrates seamlessly with existing triage systems:

1. **Synchrony Collector**: Can read and merge seeded reports with real triage data
2. **Triage Scripts**: Can overwrite seeded reports with actual diagnostic data
3. **Diagnostics Timeline API**: Serves both seeded and real data through the same endpoints
4. **Frontend Components**: Display seeded data just like real diagnostic events

## Benefits

1. **Immediate Visibility**: Dashboard shows data from first deployment
2. **No Empty States**: Eliminates "No events logged yet" messages
3. **Baseline Health**: Establishes healthy baseline for comparison
4. **Testing Foundation**: Provides initial data for testing diagnostic displays
5. **Graceful Degradation**: Real triage overwrites seeded data as it runs

## Testing

To verify the pre-seed system:

```bash
# Run pre-seed
cd bridge_backend
python3 scripts/triage_preseed.py

# Verify generated files
ls -la *_report.json unified_timeline.json

# Test synchrony collector can read seeded data
python3 scripts/synchrony_collector.py

# Clean up (these files are gitignored)
rm -f *_report.json unified_timeline.json
```

## Production Deployment

On production deployment:

1. Backend starts
2. Pre-seed runs automatically (in startup sequence)
3. Baseline reports are created
4. Unified timeline is generated
5. Other triage scripts run and may update the data
6. Frontend polls `/api/diagnostics/timeline/unified`
7. TriageBootstrapBanner confirms seeding is complete

## Maintenance

The pre-seed system requires no maintenance. It:
- Runs automatically on every deployment
- Creates disposable baseline data
- Gets overwritten by real triage results
- Has no persistent state

To manually trigger re-seeding in production:
1. Go to GitHub Actions
2. Select "Triage Pre-Seed" workflow
3. Click "Run workflow"
4. Choose the branch and confirm

## Security

- No secrets required
- No external API calls (except optional Bridge notification)
- Generates read-only baseline data
- All files are gitignored (no accidental commits)

## Performance

- Lightweight: Creates 4 small JSON files
- Fast: Completes in <1 second
- Non-blocking: Runs synchronously before triage, doesn't block server startup
- Low memory: Minimal memory footprint
