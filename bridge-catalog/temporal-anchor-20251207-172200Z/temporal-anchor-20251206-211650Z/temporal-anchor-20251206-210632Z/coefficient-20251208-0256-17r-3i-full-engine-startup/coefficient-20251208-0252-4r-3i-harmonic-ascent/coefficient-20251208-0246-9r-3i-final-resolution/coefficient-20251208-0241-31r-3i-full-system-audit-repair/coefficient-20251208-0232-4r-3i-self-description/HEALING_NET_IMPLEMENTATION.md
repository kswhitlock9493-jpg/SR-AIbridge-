# Healing Net System Implementation

## Overview

The Healing Net is a comprehensive error recovery and system resilience layer designed to prevent silent deployment failures and provide graceful degradation when services are unavailable.

## Architecture

### Core Components

#### 1. API Guardian (`healing-net.js`)
The API Guardian ensures all API calls return proper JSON and provides automatic fallback mechanisms.

**Features:**
- JSON response validation
- Automatic retry with exponential backoff
- Circuit breaker integration
- Fallback data provision
- Failure logging

**Usage:**
```javascript
import { APIGuardian } from './services/healing-net';

// Guarded API call with automatic fallback
const data = await APIGuardian.guardedApiCall('/missions', {
  baseURL: 'http://localhost:8000',
  timeout: 10000,
  retries: 2
});
```

#### 2. Umbra Lattice
Provides fallback data for offline or failing services.

**Fallback Data Available:**
- Missions
- Brain stats and memories
- Custody/Admiral keys
- Armada status
- Vault logs
- System status

#### 3. Circuit Breakers
Prevents cascade failures by opening circuits after repeated failures.

**Configuration:**
```javascript
const circuitBreaker = new CircuitBreaker('missions', {
  failureThreshold: 5,    // Open after 5 failures
  resetTimeout: 60000     // Try again after 1 minute
});
```

#### 4. Triage Engine
Monitors system health and records diagnostics.

**Features:**
- Component crash tracking
- Health monitoring
- Diagnostic recording
- Failure log management

### Frontend Integration

#### Error Boundaries
React Error Boundaries isolate component failures to prevent app-wide crashes.

**All routes are protected:**
```jsx
<Route path="/mission-log" element={
  <ErrorBoundary 
    name="MissionLog"
    errorMessage="Mission Log is temporarily unavailable."
  >
    <MissionLog />
  </ErrorBoundary>
} />
```

#### Healing Net Dashboard
Real-time monitoring dashboard showing:
- System health status
- Recent failures
- Component diagnostics
- Circuit breaker states

Access via: `/system-health` → Healing Net Dashboard section

## Backend Enhancements

### Custody Routes (Admiral Keys)
Enhanced to return proper JSON for all endpoints:

#### New Endpoints
- `GET /custody/status` - System status
- `GET /custody/keys` - List all keys
- `GET /custody/admiral` - Admiral key information
- `POST /custody/admiral/rotate` - Rotate Admiral keys

**Example Response:**
```json
{
  "status": "operational",
  "admiral_keys_initialized": true,
  "key_creation_time": "2024-01-15T10:30:00Z",
  "timestamp": "2024-01-15T10:35:00Z"
}
```

### Mission Routes
Added progress tracking and update capabilities:

#### New/Updated Endpoints
- `PATCH /missions/{mission_id}` - Update mission status, progress, etc.

**Example:**
```javascript
// Update mission progress
await updateMissionStatus(missionId, null, { progress: 75 });

// Update mission status
await updateMissionStatus(missionId, 'completed');
```

## Agent Foundry

### Features
- **Blueprint Designer** - Visual agent creation interface
- **Invisible Indoctrination** - Automatic doctrine certification
- **Quality Assurance Sanctum** - Metrics and monitoring
- **Agent Registry** - Manage all agents in one place

### Auto-Indoctrination
When enabled, agents are automatically certified with doctrine on creation:

```javascript
{
  name: "Alpha-01",
  role: "Combat",
  specialties: ["Tactics", "Navigation"],
  autoIndoctrinate: true,  // ← Invisible engine activation
  doctrineLevel: "standard"
}
```

## Mission Progress Tracking

### Real-Time Progress
Missions now support real-time progress tracking with visual progress bars:

**Features:**
- Progress percentage (0-100%)
- Visual progress bar
- Quick update controls (+10%, +25%, -10%)
- Automatic persistence

**Backend Storage:**
Mission progress is stored in the mission JSONL file and synced across all clients.

## Deployment Checklist

### Frontend
- ✅ Healing Net service layer
- ✅ API Guardian integration
- ✅ Error Boundaries on all routes
- ✅ Circuit breakers for service categories
- ✅ Healing Net Dashboard
- ✅ Agent Foundry component
- ✅ Mission progress tracking

### Backend
- ✅ Custody routes return JSON
- ✅ Brain routes return JSON (already implemented)
- ✅ Mission update endpoint
- ✅ Progress persistence

## Testing

### Frontend Testing
```bash
cd bridge-frontend
npm run lint    # Should pass with max 5 warnings
npm run build   # Should build successfully
```

### Manual Testing
1. **Navigate to System Health** - View Healing Net Dashboard
2. **Create a Mission** - Test mission creation flow
3. **Update Progress** - Test progress tracking
4. **Forge an Agent** - Test Agent Foundry with auto-indoctrination
5. **Check Admiral Keys** - Verify JSON responses
6. **Trigger Error** - Test error boundary (modify a component to throw error)

## Monitoring

### Health Status
The system reports three states:
- **Healthy** ✅ - No recent failures
- **Degraded** ⚠️ - Some failures (< 5 in last 5 minutes)
- **Unhealthy** 🚨 - Multiple failures (≥ 5 in last 5 minutes)

### Failure Logs
All API failures are logged with:
- Endpoint
- Error message
- Timestamp
- Context (status code, timeout, etc.)

### Circuit Breaker States
- **CLOSED** - Normal operation
- **OPEN** - Too many failures, using fallback
- **HALF_OPEN** - Testing if service recovered

## Configuration

### API Client
Configure in `config.js`:
```javascript
export default {
  API_BASE_URL: process.env.VITE_API_BASE_URL || 'http://localhost:8000',
  // ... other config
}
```

### Circuit Breaker Tuning
Modify thresholds in `api.js`:
```javascript
const circuitBreakers = {
  missions: new CircuitBreaker('missions', {
    failureThreshold: 5,     // Adjust threshold
    resetTimeout: 60000      // Adjust timeout
  })
}
```

## Troubleshooting

### "HTML response detected" errors
**Cause:** Backend endpoint returning HTML instead of JSON

**Solution:**
1. Verify backend route exists and is registered
2. Check CORS configuration
3. Ensure endpoint returns JSON response
4. Check backend logs for errors

### Circuit breaker keeps opening
**Cause:** Service repeatedly failing

**Solution:**
1. Check backend service is running
2. Verify endpoint functionality
3. Check network connectivity
4. Review backend logs
5. Increase threshold or timeout if transient issues

### Components keep crashing
**Cause:** Unhandled errors in component code

**Solution:**
1. Check browser console for errors
2. Review component code for null/undefined access
3. Add proper error handling
4. View Healing Net Dashboard for diagnostics

## Future Enhancements

### Planned Features
- [ ] WebSocket support for real-time mission updates
- [ ] Persistent circuit breaker state
- [ ] Advanced health metrics (response time, error rates)
- [ ] Automatic recovery suggestions
- [ ] Alert notifications for critical failures
- [ ] Mission templates
- [ ] Batch operations for agents

### Performance Optimizations
- [ ] Request deduplication
- [ ] Response caching
- [ ] Lazy loading for large datasets
- [ ] Virtual scrolling for long lists

## API Reference

See individual component documentation for detailed API usage:
- `healing-net.js` - Core healing net services
- `ErrorBoundary.jsx` - React error boundary component
- `HealingNetDashboard.jsx` - Monitoring dashboard
- `AgentFoundry.jsx` - Agent creation and management
- `MissionLog.jsx` - Mission tracking with progress
