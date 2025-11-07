import { useState, useEffect } from 'react';
import { 
  getSystemHealth, 
  getSystemHealthFull,
  runSelfTest, 
  runSelfRepair, 
  getSystemMetrics 
} from '../api';
import HealingNetDashboard from './HealingNetDashboard.jsx';

const SystemSelfTest = () => {
  const [healthStatus, setHealthStatus] = useState(null);
  const [fullHealthData, setFullHealthData] = useState(null);
  const [systemMetrics, setSystemMetrics] = useState(null);
  const [testResults, setTestResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isAutoRefresh, setIsAutoRefresh] = useState(true);
  const [lastUpdate, setLastUpdate] = useState(new Date());
  const [testHistory, setTestHistory] = useState([]);

  // Fetch all health data
  const fetchHealthData = async () => {
    try {
      setError(null);
      
      const [health, fullHealth, metrics] = await Promise.allSettled([
        getSystemHealth(),
        getSystemHealthFull(),
        getSystemMetrics()
      ]);

      if (health.status === 'fulfilled') {
        setHealthStatus(health.value);
      }
      if (fullHealth.status === 'fulfilled') {
        setFullHealthData(fullHealth.value);
      }
      if (metrics.status === 'fulfilled') {
        setSystemMetrics(metrics.value);
      }

      setLastUpdate(new Date());
    } catch (err) {
      console.error('Failed to fetch health data:', err);
      setError('Failed to load health data: ' + err.message);
    }
  };

  // Run system self-test
  const handleRunSelfTest = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const result = await runSelfTest();
      setTestResults(result);
      
      // Add to test history
      const testEntry = {
        id: Date.now(),
        timestamp: new Date().toISOString(),
        type: 'self-test',
        result: result,
        status: result.status || 'completed'
      };
      setTestHistory(prev => [testEntry, ...prev.slice(0, 9)]); // Keep last 10 tests
      
      // Refresh health data after test
      await fetchHealthData();
    } catch (err) {
      console.error('Self-test failed:', err);
      setError('Self-test failed: ' + err.message);
      
      const testEntry = {
        id: Date.now(),
        timestamp: new Date().toISOString(),
        type: 'self-test',
        result: null,
        status: 'failed',
        error: err.message
      };
      setTestHistory(prev => [testEntry, ...prev.slice(0, 9)]);
    } finally {
      setLoading(false);
    }
  };

  // Run system self-repair
  const handleRunSelfRepair = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const result = await runSelfRepair();
      
      // Add to test history
      const testEntry = {
        id: Date.now(),
        timestamp: new Date().toISOString(),
        type: 'self-repair',
        result: result,
        status: result.status || 'completed'
      };
      setTestHistory(prev => [testEntry, ...prev.slice(0, 9)]);
      
      // Refresh health data after repair
      await fetchHealthData();
    } catch (err) {
      console.error('Self-repair failed:', err);
      setError('Self-repair failed: ' + err.message);
      
      const testEntry = {
        id: Date.now(),
        timestamp: new Date().toISOString(),
        type: 'self-repair',
        result: null,
        status: 'failed',
        error: err.message
      };
      setTestHistory(prev => [testEntry, ...prev.slice(0, 9)]);
    } finally {
      setLoading(false);
    }
  };

  // Get status color
  const getStatusColor = (status) => {
    switch (status) {
      case 'healthy':
      case 'operational':
      case 'online':
      case 'passed':
        return '#28a745';
      case 'degraded':
      case 'warning':
        return '#ffc107';
      case 'unhealthy':
      case 'critical':
      case 'failed':
      case 'offline':
        return '#dc3545';
      default:
        return '#6c757d';
    }
  };

  // Get status icon
  const getStatusIcon = (status) => {
    switch (status) {
      case 'healthy':
      case 'operational':
      case 'online':
      case 'passed':
        return '✅';
      case 'degraded':
      case 'warning':
        return '⚠️';
      case 'unhealthy':
      case 'critical':
      case 'failed':
      case 'offline':
        return '❌';
      default:
        return '❓';
    }
  };

  // Format timestamp
  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    return {
      date: date.toLocaleDateString(),
      time: date.toLocaleTimeString()
    };
  };

  // Initial load and auto-refresh
  useEffect(() => {
    fetchHealthData();
    
    let interval;
    if (isAutoRefresh) {
      interval = setInterval(fetchHealthData, 30000); // Refresh every 30 seconds
    }
    
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isAutoRefresh]);

  return (
    <div className="system-self-test">
      <div className="self-test-header">
        <h2>🔍 System Self-Test & Health Monitor</h2>
        <div className="header-actions">
          <div className="auto-refresh-toggle">
            <label>
              <input
                type="checkbox"
                checked={isAutoRefresh}
                onChange={(e) => setIsAutoRefresh(e.target.checked)}
              />
              Auto-refresh
            </label>
          </div>
          <span className="last-update">
            Last Updated: {lastUpdate.toLocaleTimeString()}
          </span>
          <button onClick={fetchHealthData} className="refresh-btn">
            🔄 Refresh
          </button>
        </div>
      </div>

      {error && (
        <div className="error-banner">
          <span>⚠️</span>
          <span>{error}</span>
          <button onClick={() => setError(null)}>✕</button>
        </div>
      )}

      {/* Main Control Panel */}
      <div className="control-panel">
        <div className="control-actions">
          <button
            onClick={handleRunSelfTest}
            disabled={loading}
            className="action-btn self-test"
          >
            {loading ? '⏳ Running...' : '🔍 Run Self-Test'}
          </button>
          <button
            onClick={handleRunSelfRepair}
            disabled={loading}
            className="action-btn self-repair"
          >
            {loading ? '⏳ Repairing...' : '🔧 Run Self-Repair'}
          </button>
          <button
            onClick={fetchHealthData}
            disabled={loading}
            className="action-btn refresh"
          >
            🔄 Refresh Status
          </button>
        </div>
      </div>

      <div className="health-dashboard">
        {/* System Health Overview */}
        <div className="health-overview">
          <h3>🏥 System Health Overview</h3>
          {healthStatus ? (
            <div className="health-summary">
              <div
                className="overall-status"
                style={{ backgroundColor: getStatusColor(healthStatus.status) }}
              >
                <span className="status-icon">
                  {getStatusIcon(healthStatus.status)}
                </span>
                <span className="status-text">
                  {healthStatus.status?.toUpperCase() || 'UNKNOWN'}
                </span>
              </div>
              <div className="health-details">
                {Object.entries(healthStatus).map(([key, value]) => (
                  key !== 'status' && (
                    <div key={key} className="health-detail">
                      <span className="detail-label">{key.replace(/_/g, ' ')}:</span>
                      <span className="detail-value">
                        {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                      </span>
                    </div>
                  )
                ))}
              </div>
            </div>
          ) : (
            <div className="no-data">No health data available</div>
          )}
        </div>

        {/* Detailed Health Information */}
        {fullHealthData && (
          <div className="detailed-health">
            <h3>🔬 Detailed Health Analysis</h3>
            <div className="health-components">
              {fullHealthData.components ? (
                Object.entries(fullHealthData.components).map(([component, data]) => (
                  <div key={component} className="component-health">
                    <div className="component-header">
                      <span className="component-name">{component}</span>
                      <span
                        className="component-status"
                        style={{ backgroundColor: getStatusColor(data.status) }}
                      >
                        {getStatusIcon(data.status)} {data.status}
                      </span>
                    </div>
                    {data.details && (
                      <div className="component-details">
                        {Object.entries(data.details).map(([key, value]) => (
                          <div key={key} className="detail-item">
                            <span>{key}:</span>
                            <span>{String(value)}</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                ))
              ) : (
                <div className="health-raw">
                  <pre>{JSON.stringify(fullHealthData, null, 2)}</pre>
                </div>
              )}
            </div>
          </div>
        )}

        {/* System Metrics */}
        {systemMetrics && (
          <div className="system-metrics">
            <h3>📊 System Metrics</h3>
            <div className="metrics-grid">
              {Object.entries(systemMetrics).map(([key, value]) => (
                <div key={key} className="metric-item">
                  <div className="metric-label">{key.replace(/_/g, ' ')}</div>
                  <div className="metric-value">
                    {typeof value === 'number' ? value.toFixed(2) : String(value)}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Latest Test Results */}
        {testResults && (
          <div className="test-results">
            <h3>🧪 Latest Test Results</h3>
            <div className="results-container">
              <div className="results-summary">
                <span
                  className="results-status"
                  style={{ backgroundColor: getStatusColor(testResults.status) }}
                >
                  {getStatusIcon(testResults.status)} {testResults.status?.toUpperCase()}
                </span>
                <span className="results-timestamp">
                  {formatTimestamp(testResults.timestamp || Date.now()).time}
                </span>
              </div>
              <div className="results-details">
                <pre>{JSON.stringify(testResults, null, 2)}</pre>
              </div>
            </div>
          </div>
        )}

        {/* Test History */}
        <div className="test-history">
          <h3>📋 Test History</h3>
          <div className="history-list">
            {testHistory.length > 0 ? (
              testHistory.map((test) => {
                const { date, time } = formatTimestamp(test.timestamp);
                return (
                  <div key={test.id} className="history-item">
                    <div className="history-header">
                      <span className="test-type">
                        {test.type === 'self-test' ? '🔍' : '🔧'} {test.type}
                      </span>
                      <span
                        className="test-status"
                        style={{ backgroundColor: getStatusColor(test.status) }}
                      >
                        {getStatusIcon(test.status)} {test.status}
                      </span>
                      <span className="test-time">{date} {time}</span>
                    </div>
                    {test.error && (
                      <div className="test-error">
                        ❌ {test.error}
                      </div>
                    )}
                    {test.result && (
                      <div className="test-result">
                        <details>
                          <summary>View Results</summary>
                          <pre>{JSON.stringify(test.result, null, 2)}</pre>
                        </details>
                      </div>
                    )}
                  </div>
                );
              })
            ) : (
              <div className="no-history">
                <span>📋</span>
                <p>No test history available. Run a self-test to get started.</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* System Information */}
      <div className="system-info">
        <h4>ℹ️ System Information</h4>
        <div className="info-grid">
          <div className="info-item">
            <span>Health Endpoint:</span>
            <span>/health</span>
          </div>
          <div className="info-item">
            <span>Full Health Endpoint:</span>
            <span>/health/full</span>
          </div>
          <div className="info-item">
            <span>Metrics Endpoint:</span>
            <span>/system/metrics</span>
          </div>
          <div className="info-item">
            <span>Auto-refresh:</span>
            <span>{isAutoRefresh ? 'Enabled (30s)' : 'Disabled'}</span>
          </div>
        </div>
      </div>

      {/* Healing Net Dashboard Integration */}
      <HealingNetDashboard />
    </div>
  );
};

export default SystemSelfTest;