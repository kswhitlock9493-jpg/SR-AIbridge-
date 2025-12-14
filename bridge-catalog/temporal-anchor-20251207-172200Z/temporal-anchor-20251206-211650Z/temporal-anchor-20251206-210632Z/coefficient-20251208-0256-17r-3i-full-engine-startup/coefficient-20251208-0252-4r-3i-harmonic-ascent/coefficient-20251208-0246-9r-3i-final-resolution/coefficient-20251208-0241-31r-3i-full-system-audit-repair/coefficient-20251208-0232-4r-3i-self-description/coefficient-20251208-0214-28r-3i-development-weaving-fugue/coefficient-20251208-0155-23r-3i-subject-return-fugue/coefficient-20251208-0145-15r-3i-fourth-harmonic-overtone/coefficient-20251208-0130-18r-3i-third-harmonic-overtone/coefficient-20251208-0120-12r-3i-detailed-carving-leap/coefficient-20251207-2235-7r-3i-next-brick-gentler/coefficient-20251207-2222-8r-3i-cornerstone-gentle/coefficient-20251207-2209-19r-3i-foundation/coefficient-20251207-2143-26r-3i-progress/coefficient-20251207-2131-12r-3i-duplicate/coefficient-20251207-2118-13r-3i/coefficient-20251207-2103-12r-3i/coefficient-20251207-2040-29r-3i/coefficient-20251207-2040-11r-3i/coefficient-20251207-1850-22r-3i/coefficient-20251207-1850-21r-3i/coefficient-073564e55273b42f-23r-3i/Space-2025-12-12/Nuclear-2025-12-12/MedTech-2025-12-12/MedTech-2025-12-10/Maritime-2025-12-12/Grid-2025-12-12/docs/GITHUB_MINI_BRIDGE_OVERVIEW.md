# GitHub Mini-Bridge Overview

## 🚀 Internal Self-Governance Engine

The GitHub Mini-Bridge is a compact, self-contained instance of the SR-AIbridge engine that runs entirely within GitHub Actions. It provides autonomous monitoring, repair, and certification capabilities without relying on external services.

## Architecture

### Traditional Bridge vs Mini-Bridge

**Traditional Bridge**:
```
GitHub → (Network) → Render/Netlify → Bridge Backend → Database
```

**Mini-Bridge**:
```
GitHub → .github/autonomy_node/ → Local Reports
```

### Advantages

1. **Zero External Dependencies**: Operates entirely within GitHub's infrastructure
2. **No Network Latency**: Direct access to repository files
3. **Continuous Availability**: Not affected by external service outages
4. **Cost Effective**: Uses GitHub Actions minutes only
5. **Security**: Runs in GitHub's secure sandbox environment

## Components

### 1. Autonomy Core (`core.py`)

The orchestration engine that coordinates all operations:

- Schedules scans and repairs
- Manages component lifecycle
- Generates audit reports
- Handles Genesis Bus integration

### 2. Truth Micro-Certifier (`truth.py`)

Lightweight version of the Truth Engine:

- Validates repair results
- Ensures changes meet quality standards
- Prevents infinite repair loops
- Issues certification or warnings

### 3. Parser Sentinel (`parser.py`)

Repository scanning engine:

- Walks file tree systematically
- Identifies code patterns
- Detects potential issues
- Reports findings for review

### 4. Blueprint Micro-Forge (`blueprint.py`)

Safe repair pattern engine:

- Applies pre-approved fixes
- Follows deterministic rules
- Maintains code integrity
- Logs all changes

### 5. Cascade Mini-Orchestrator (`cascade.py`)

State synchronization engine:

- Syncs with main Cascade engine (when online)
- Maintains rollback capability
- Ensures consistency
- Tracks change history

## Operational Modes

### 1. Online Mode

When external Bridge is reachable:

- Reports to Genesis Bus
- Syncs with Cascade Engine
- Coordinates with other engines
- Full telemetry enabled

### 2. Offline Mode

When external Bridge is unreachable:

- Stores reports locally
- Continues autonomous operation
- Queues events for later sync
- Maintains full functionality

### 3. Hybrid Mode

Partial connectivity:

- Opportunistic sync
- Graceful degradation
- Local caching
- Smart retry logic

## Scheduling

### Automatic Triggers

1. **Push Events**: Every commit to main branch
2. **Scheduled**: Every 6 hours via cron
3. **Manual**: Workflow dispatch button

### Execution Flow

```
Trigger → Setup Python → Run core.py → Generate Report
```

### Timing Strategy

- **Staggered from External Bridge**: Runs offset from main autonomy cycle
- **Non-blocking**: Uses `continue-on-error: true`
- **Quick execution**: Typically completes in < 2 minutes
- **Resource efficient**: Minimal GitHub Actions minutes usage

## Security Model

### GitHub Actions Sandbox

- **Read-only by default**: No write access to repository
- **Isolated environment**: Clean workspace on each run
- **Secrets protection**: No access to repository secrets
- **Network isolation**: Limited external connectivity

### RBAC Integration

While the node runs in CI, its configuration is governed by RBAC:

- **Admiral**: Can modify `node_config.json`
- **Captain**: Can trigger manual runs
- **Observer**: Can view reports

### Safety Mechanisms

1. **Truth Certification**: All changes validated before application
2. **Dry-run Mode**: Preview changes without applying
3. **Rollback Support**: Changes can be reverted via Cascade
4. **Audit Trail**: All actions logged in reports

## Telemetry & Monitoring

### Local Reports

Stored in `.github/autonomy_node/reports/`:

```
summary_20251013.json
summary_20251014.json
summary_20251015.json
```

### Report Structure

```json
{
  "timestamp": "2025-10-13T12:00:00.000000",
  "version": "1.9.7n",
  "findings_count": 10,
  "fixes_count": 8,
  "findings": {
    "file1.py": {
      "status": "warn",
      "reason": "debug print",
      "path": "./src/file1.py"
    }
  },
  "fixes": {
    "file1.py": {
      "status": "ok",
      "action": "log_cleaned"
    }
  },
  "status": "complete"
}
```

### Genesis Bus Events

When online, publishes rich telemetry:

- **Registration**: Node startup and health
- **Scan Results**: Findings and statistics
- **Repair Actions**: Changes applied
- **Verification**: Truth certification results
- **Synchronization**: Cascade sync status

## Failure Modes & Recovery

### Scenario 1: External Bridge Down

**Detection**: Genesis Bus unreachable  
**Response**: Switch to offline mode  
**Recovery**: Queue events for later sync

### Scenario 2: Parser Error

**Detection**: Exception in scan_repo()  
**Response**: Log error, continue with partial results  
**Recovery**: Retry on next run

### Scenario 3: Truth Certification Failure

**Detection**: verify() returns warnings  
**Response**: Abort changes, log details  
**Recovery**: Manual review required

### Scenario 4: Configuration Corruption

**Detection**: Invalid node_config.json  
**Response**: Fall back to defaults  
**Recovery**: Restore from git history

## Performance Characteristics

### Resource Usage

- **CPU**: Minimal (< 1 CPU minute per run)
- **Memory**: ~50-100 MB
- **Storage**: ~1 KB per report
- **Network**: Minimal (Genesis Bus only)

### Execution Time

- **Small repos** (< 100 files): 10-30 seconds
- **Medium repos** (100-1000 files): 30-90 seconds
- **Large repos** (> 1000 files): 90-180 seconds

### Scalability

- **File limit**: Handles repos with 10,000+ files
- **Parallel execution**: Single-threaded (GitHub Actions limitation)
- **Report retention**: Configurable (default: 10 backups)

## Integration Points

### Genesis Bus

```python
await genesis_bus.publish("genesis.autonomy_node.report", {
    "findings": findings,
    "fixes": fixes,
    "timestamp": datetime.utcnow().isoformat()
})
```

### Cascade Engine

```python
from bridge_backend.engines.cascade.service import CascadeEngine

cascade = CascadeEngine()
await cascade.sync_state()
```

### Truth Engine

```python
from bridge_backend.engines.truth import verify_integrity

result = verify_integrity(changes)
```

## Best Practices

### Configuration

1. **Set appropriate intervals**: Balance monitoring vs. resource usage
2. **Enable Genesis registration**: For full telemetry
3. **Limit report backups**: Prevent repo bloat
4. **Use truth certification**: Ensure change quality

### Monitoring

1. **Review reports regularly**: Check `.github/autonomy_node/reports/`
2. **Monitor workflow runs**: GitHub Actions tab
3. **Subscribe to Genesis events**: Real-time notifications
4. **Set up alerts**: For repeated failures

### Maintenance

1. **Prune old reports**: Prevent accumulation
2. **Update configuration**: As needs change
3. **Review scan patterns**: Adjust parser rules
4. **Test manually**: Before relying on automation

## Comparison with Full Bridge

| Feature | Full Bridge | Mini-Bridge |
|---------|-------------|-------------|
| Deployment | Render/Netlify | GitHub Actions |
| Database | PostgreSQL | File-based reports |
| API | REST + WebSocket | None (internal) |
| Genesis Bus | Full integration | Best-effort |
| Cascade | Full rollback | Sync-only |
| Truth | Full certification | Micro-certifier |
| Blueprint | Full planning | Pattern-based |
| RBAC | Full enforcement | Config-based |
| Cost | Hosting fees | Actions minutes |
| Availability | Network-dependent | Always available |

## Future Enhancements

### Planned Features

- [ ] Enhanced parser rules
- [ ] More repair patterns
- [ ] Integration with GitHub Checks API
- [ ] Pull request commenting
- [ ] Automatic issue creation
- [ ] Metrics dashboard
- [ ] Alert notifications
- [ ] Multi-repo support

### Experimental

- [ ] AI-powered pattern detection
- [ ] Predictive issue detection
- [ ] Automatic dependency updates
- [ ] Security vulnerability scanning
- [ ] Code quality metrics
- [ ] Performance profiling

## Troubleshooting

### Common Issues

**Issue**: Node not running  
**Fix**: Check `.github/workflows/autonomy_node.yml` syntax

**Issue**: Reports not generated  
**Fix**: Ensure `reports/` directory exists and is writable

**Issue**: Genesis Bus connection fails  
**Fix**: Normal in offline mode; check external Bridge status

**Issue**: Parser too slow  
**Fix**: Add directory exclusions in `parser.py`

**Issue**: Too many findings  
**Fix**: Adjust thresholds in `node_config.json`

## See Also

- [Embedded Autonomy Node Documentation](EMBEDDED_AUTONOMY_NODE.md)
- [Node Failsafe Guide](NODE_FAILSAFE_GUIDE.md)
- [Total Autonomy Protocol](TOTAL_AUTONOMY_PROTOCOL.md)
- [Genesis Bus Documentation](GENESIS_V2_GUIDE.md)
