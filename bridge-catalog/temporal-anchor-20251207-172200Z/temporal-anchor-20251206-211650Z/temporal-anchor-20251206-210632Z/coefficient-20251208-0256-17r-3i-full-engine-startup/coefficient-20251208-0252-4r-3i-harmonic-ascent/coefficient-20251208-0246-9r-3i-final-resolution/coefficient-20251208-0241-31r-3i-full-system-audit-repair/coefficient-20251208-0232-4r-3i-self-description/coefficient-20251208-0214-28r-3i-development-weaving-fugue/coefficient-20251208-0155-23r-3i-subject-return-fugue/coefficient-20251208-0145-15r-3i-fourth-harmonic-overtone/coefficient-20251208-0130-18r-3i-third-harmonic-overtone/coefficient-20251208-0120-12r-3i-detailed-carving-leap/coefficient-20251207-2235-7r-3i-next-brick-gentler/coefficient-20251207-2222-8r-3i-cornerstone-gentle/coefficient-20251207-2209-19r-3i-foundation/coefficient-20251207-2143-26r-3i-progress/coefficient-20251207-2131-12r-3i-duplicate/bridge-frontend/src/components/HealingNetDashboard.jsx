import { useState, useEffect } from 'react';
import { TriageEngine } from '../services/healing-net';

/**
 * Healing Net Dashboard - System Health Monitoring
 * Displays diagnostics, failure logs, and circuit breaker states
 */
const HealingNetDashboard = () => {
  const [diagnostics, setDiagnostics] = useState({ diagnostics: [], monitors: [], failureLog: [] });
  const [showDetails, setShowDetails] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(true);

  useEffect(() => {
    const updateDiagnostics = () => {
      const data = TriageEngine.getDiagnostics();
      setDiagnostics(data);
    };

    updateDiagnostics();

    if (autoRefresh) {
      const interval = setInterval(updateDiagnostics, 5000); // Update every 5 seconds
      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  const handleClearDiagnostics = () => {
    TriageEngine.clearDiagnostics();
    setDiagnostics({ diagnostics: [], monitors: [], failureLog: [] });
  };

  const getHealthStatus = () => {
    const recentFailures = diagnostics.failureLog.filter(f => {
      const failTime = new Date(f.timestamp);
      const now = new Date();
      return (now - failTime) < 5 * 60 * 1000; // Last 5 minutes
    }).length;

    if (recentFailures === 0) return { status: 'healthy', color: '#4CAF50', icon: '✅' };
    if (recentFailures < 5) return { status: 'degraded', color: '#ff9800', icon: '⚠️' };
    return { status: 'unhealthy', color: '#f44336', icon: '🚨' };
  };

  const health = getHealthStatus();

  return (
    <div className="healing-net-dashboard panel" style={{ marginTop: '20px' }}>
      <div className="panel-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h3>🩺 Healing Net Dashboard</h3>
          <p style={{ margin: '4px 0', fontSize: '14px', color: '#666' }}>
            System Health Monitoring & Triage
          </p>
        </div>
        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '14px' }}>
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
            />
            Auto-refresh
          </label>
          <button
            onClick={handleClearDiagnostics}
            style={{
              padding: '6px 12px',
              backgroundColor: '#2196F3',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '12px'
            }}
          >
            🗑️ Clear Logs
          </button>
        </div>
      </div>

      {/* Overall Health Status */}
      <div style={{
        padding: '16px',
        backgroundColor: `${health.color}15`,
        borderRadius: '8px',
        border: `2px solid ${health.color}`,
        marginBottom: '16px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <span style={{ fontSize: '32px' }}>{health.icon}</span>
          <div>
            <div style={{ fontSize: '18px', fontWeight: 'bold', color: health.color, textTransform: 'uppercase' }}>
              System {health.status}
            </div>
            <div style={{ fontSize: '14px', color: '#666' }}>
              {diagnostics.failureLog.length} total failures logged
            </div>
          </div>
        </div>
      </div>

      {/* Health Monitors */}
      {diagnostics.monitors.length > 0 && (
        <div style={{ marginBottom: '16px' }}>
          <h4>📊 Health Monitors</h4>
          <div style={{ display: 'grid', gap: '8px' }}>
            {diagnostics.monitors.map((monitor, idx) => (
              <div
                key={idx}
                style={{
                  padding: '12px',
                  backgroundColor: 'rgba(255, 255, 255, 0.05)',
                  borderRadius: '4px',
                  border: '1px solid rgba(255, 255, 255, 0.1)'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <strong>{monitor.name}</strong>
                  <span style={{
                    padding: '2px 8px',
                    backgroundColor: monitor.lastStatus?.healthy ? '#4CAF50' : '#f44336',
                    color: 'white',
                    borderRadius: '4px',
                    fontSize: '11px'
                  }}>
                    {monitor.lastStatus?.healthy ? 'HEALTHY' : 'UNHEALTHY'}
                  </span>
                </div>
                {monitor.lastCheck && (
                  <div style={{ fontSize: '12px', color: '#999', marginTop: '4px' }}>
                    Last check: {new Date(monitor.lastCheck).toLocaleTimeString()}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recent Failures */}
      {diagnostics.failureLog.length > 0 && (
        <div style={{ marginBottom: '16px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
            <h4>🚨 Recent Failures ({diagnostics.failureLog.slice(-10).length})</h4>
            <button
              onClick={() => setShowDetails(!showDetails)}
              style={{
                padding: '4px 8px',
                backgroundColor: 'transparent',
                color: '#2196F3',
                border: '1px solid #2196F3',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '12px'
              }}
            >
              {showDetails ? 'Hide Details' : 'Show Details'}
            </button>
          </div>
          
          <div style={{ display: 'grid', gap: '8px' }}>
            {diagnostics.failureLog.slice(-10).reverse().map((failure, idx) => (
              <div
                key={idx}
                style={{
                  padding: '12px',
                  backgroundColor: 'rgba(244, 67, 54, 0.1)',
                  borderRadius: '4px',
                  border: '1px solid rgba(244, 67, 54, 0.3)'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                  <strong style={{ color: '#f44336' }}>{failure.endpoint}</strong>
                  <span style={{ fontSize: '12px', color: '#999' }}>
                    {new Date(failure.timestamp).toLocaleString()}
                  </span>
                </div>
                <div style={{ fontSize: '14px', color: '#666' }}>{failure.error}</div>
                
                {showDetails && failure.context && Object.keys(failure.context).length > 0 && (
                  <details style={{ marginTop: '8px' }}>
                    <summary style={{ cursor: 'pointer', fontSize: '12px', color: '#999' }}>
                      Context
                    </summary>
                    <pre style={{
                      marginTop: '8px',
                      padding: '8px',
                      backgroundColor: 'rgba(0, 0, 0, 0.2)',
                      borderRadius: '4px',
                      fontSize: '11px',
                      overflow: 'auto'
                    }}>
                      {JSON.stringify(failure.context, null, 2)}
                    </pre>
                  </details>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Component Diagnostics */}
      {diagnostics.diagnostics.length > 0 && (
        <div>
          <h4>🔍 Component Diagnostics ({diagnostics.diagnostics.slice(-10).length})</h4>
          <div style={{ display: 'grid', gap: '8px' }}>
            {diagnostics.diagnostics.slice(-10).reverse().map((diag, idx) => (
              <div
                key={idx}
                style={{
                  padding: '12px',
                  backgroundColor: diag.status === 'unhealthy' || diag.type === 'component_crash'
                    ? 'rgba(244, 67, 54, 0.1)'
                    : 'rgba(255, 152, 0, 0.1)',
                  borderRadius: '4px',
                  border: `1px solid ${
                    diag.status === 'unhealthy' || diag.type === 'component_crash'
                      ? 'rgba(244, 67, 54, 0.3)'
                      : 'rgba(255, 152, 0, 0.3)'
                  }`
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                  <strong>{diag.component}</strong>
                  <span style={{ fontSize: '12px', color: '#999' }}>
                    {new Date(diag.timestamp).toLocaleString()}
                  </span>
                </div>
                <div style={{ fontSize: '14px', color: '#666' }}>
                  {diag.type === 'component_crash' ? '💥 Component Crash' : `Status: ${diag.status}`}
                </div>
                {diag.error && (
                  <div style={{ fontSize: '13px', color: '#f44336', marginTop: '4px' }}>
                    {diag.error}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {diagnostics.failureLog.length === 0 && diagnostics.diagnostics.length === 0 && (
        <div style={{ textAlign: 'center', padding: '40px', color: '#666' }}>
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>✅</div>
          <div style={{ fontSize: '18px', fontWeight: 'bold', marginBottom: '8px' }}>
            All Systems Operational
          </div>
          <div style={{ fontSize: '14px' }}>
            No failures or issues detected. Healing Net is standing by.
          </div>
        </div>
      )}
    </div>
  );
};

export default HealingNetDashboard;
