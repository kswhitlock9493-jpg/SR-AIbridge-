import React, { useState, useEffect } from 'react';
import { 
  runSelfTest, 
  runSelfRepair, 
  getSystemMetrics, 
  getSystemHealth, 
  getSystemHealthFull 
} from '../api';

const SystemSelfTest = () => {
  const [healthStatus, setHealthStatus] = useState(null);
  const [fullHealth, setFullHealth] = useState(null);
  const [metrics, setMetrics] = useState(null);
  const [selfTestResult, setSelfTestResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isAutoRefresh, setIsAutoRefresh] = useState(true);
  const [lastUpdate, setLastUpdate] = useState(null);

  // Auto-refresh health status every 30 seconds
  useEffect(() => {
    const fetchHealthData = async () => {
      try {
        const [health, fullHealthData, metricsData] = await Promise.all([
          getSystemHealth().catch(() => ({ status: 'error', error: 'Failed to fetch basic health' })),
          getSystemHealthFull().catch(() => ({ status: 'error', error: 'Failed to fetch full health' })),
          getSystemMetrics().catch(() => ({ status: 'error', error: 'Failed to fetch metrics' }))
        ]);

        setHealthStatus(health);
        setFullHealth(fullHealthData);
        setMetrics(metricsData);
        setLastUpdate(new Date());
      } catch (error) {
        console.error('Error fetching health data:', error);
      }
    };

    // Initial fetch
    fetchHealthData();

    // Set up auto-refresh if enabled
    let interval;
    if (isAutoRefresh) {
      interval = setInterval(fetchHealthData, 30000); // 30 seconds
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isAutoRefresh]);

  const handleSelfTest = async () => {
    setIsLoading(true);
    try {
      const result = await runSelfTest();
      setSelfTestResult(result);
    } catch (error) {
      setSelfTestResult({
        status: 'failed',
        message: 'Self-test failed to execute',
        error: error.message,
        timestamp: new Date().toISOString()
      });
    }
    setIsLoading(false);
  };

  const handleSelfRepair = async () => {
    setIsLoading(true);
    try {
      const result = await runSelfRepair();
      setSelfTestResult(result);
      // Refresh health data after repair
      setTimeout(() => window.location.reload(), 2000);
    } catch (error) {
      setSelfTestResult({
        status: 'failed',
        message: 'Self-repair failed to execute',
        error: error.message,
        timestamp: new Date().toISOString()
      });
    }
    setIsLoading(false);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'healthy':
      case 'ok':
      case 'passed':
      case 'success':
        return '#10b981'; // green
      case 'degraded':
      case 'warning':
        return '#f59e0b'; // amber
      case 'unhealthy':
      case 'error':
      case 'failed':
        return '#ef4444'; // red
      default:
        return '#6b7280'; // gray
    }
  };

  const formatTimestamp = (timestamp) => {
    if (!timestamp) return 'Unknown';
    try {
      return new Date(timestamp).toLocaleString();
    } catch {
      return timestamp;
    }
  };

  return (
    <div style={{ 
      padding: '20px', 
      fontFamily: 'monospace', 
      backgroundColor: '#1a1a1a', 
      color: '#e0e0e0',
      borderRadius: '8px',
      border: '1px solid #333'
    }}>
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center', 
        marginBottom: '20px' 
      }}>
        <h2 style={{ color: '#00ff88', margin: 0 }}>🛡️ System Self-Test & Health Monitor</h2>
        <div>
          <label style={{ marginRight: '10px' }}>
            <input
              type="checkbox"
              checked={isAutoRefresh}
              onChange={(e) => setIsAutoRefresh(e.target.checked)}
              style={{ marginRight: '5px' }}
            />
            Auto-refresh (30s)
          </label>
          {lastUpdate && (
            <span style={{ fontSize: '12px', color: '#888' }}>
              Last updated: {lastUpdate.toLocaleTimeString()}
            </span>
          )}
        </div>
      </div>

      {/* Health Status Cards */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', 
        gap: '15px', 
        marginBottom: '20px' 
      }}>
        {/* Basic Health */}
        <div style={{ 
          padding: '15px', 
          backgroundColor: '#2a2a2a', 
          borderRadius: '6px', 
          border: `2px solid ${getStatusColor(healthStatus?.status)}` 
        }}>
          <h3 style={{ 
            color: getStatusColor(healthStatus?.status), 
            margin: '0 0 10px 0', 
            fontSize: '16px' 
          }}>
            🚀 System Status
          </h3>
          {healthStatus ? (
            <div>
              <div><strong>Status:</strong> {healthStatus.status}</div>
              <div><strong>Service:</strong> {healthStatus.service}</div>
              <div><strong>Version:</strong> {healthStatus.version}</div>
              <div><strong>Database:</strong> {healthStatus.database || 'unknown'}</div>
              {healthStatus.timestamp && (
                <div style={{ fontSize: '12px', color: '#888', marginTop: '5px' }}>
                  {formatTimestamp(healthStatus.timestamp)}
                </div>
              )}
            </div>
          ) : (
            <div style={{ color: '#888' }}>Loading...</div>
          )}
        </div>

        {/* Full Health */}
        <div style={{ 
          padding: '15px', 
          backgroundColor: '#2a2a2a', 
          borderRadius: '6px', 
          border: `2px solid ${getStatusColor(fullHealth?.status)}` 
        }}>
          <h3 style={{ 
            color: getStatusColor(fullHealth?.status), 
            margin: '0 0 10px 0', 
            fontSize: '16px' 
          }}>
            🔍 Detailed Health
          </h3>
          {fullHealth ? (
            <div>
              <div><strong>Overall:</strong> {fullHealth.status}</div>
              {fullHealth.components && (
                <div style={{ marginTop: '10px' }}>
                  <div style={{ fontSize: '14px', fontWeight: 'bold', marginBottom: '5px' }}>Components:</div>
                  {Object.entries(fullHealth.components).map(([key, value]) => (
                    <div key={key} style={{ fontSize: '12px', marginLeft: '10px' }}>
                      <span style={{ color: getStatusColor(value?.status) }}>●</span> {key}: {value?.status || 'unknown'}
                    </div>
                  ))}
                </div>
              )}
              {fullHealth.self_heal_available && (
                <div style={{ 
                  fontSize: '12px', 
                  color: '#10b981', 
                  marginTop: '5px' 
                }}>
                  🔧 Self-heal available
                </div>
              )}
            </div>
          ) : (
            <div style={{ color: '#888' }}>Loading...</div>
          )}
        </div>

        {/* Metrics */}
        <div style={{ 
          padding: '15px', 
          backgroundColor: '#2a2a2a', 
          borderRadius: '6px', 
          border: '2px solid #6b7280' 
        }}>
          <h3 style={{ 
            color: '#60a5fa', 
            margin: '0 0 10px 0', 
            fontSize: '16px' 
          }}>
            📊 System Metrics
          </h3>
          {metrics ? (
            <div>
              {metrics.metrics?.database && (
                <div>
                  <div><strong>Health Score:</strong> {metrics.metrics.database.health_score}%</div>
                  <div><strong>Connection:</strong> {metrics.metrics.database.connection_status}</div>
                  {metrics.metrics.database.record_counts && (
                    <div style={{ marginTop: '5px', fontSize: '12px' }}>
                      <strong>Records:</strong>
                      {Object.entries(metrics.metrics.database.record_counts).map(([key, value]) => (
                        <div key={key} style={{ marginLeft: '10px' }}>
                          {key}: {value}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
              {metrics.metrics?.system && (
                <div style={{ marginTop: '10px', fontSize: '12px' }}>
                  <div><strong>Version:</strong> {metrics.metrics.system.version}</div>
                  <div><strong>CORS:</strong> {metrics.metrics.system.cors_configured ? '✅' : '❌'}</div>
                </div>
              )}
            </div>
          ) : (
            <div style={{ color: '#888' }}>Loading...</div>
          )}
        </div>
      </div>

      {/* Action Buttons */}
      <div style={{ 
        display: 'flex', 
        gap: '10px', 
        marginBottom: '20px',
        flexWrap: 'wrap'
      }}>
        <button
          onClick={handleSelfTest}
          disabled={isLoading}
          style={{
            padding: '10px 20px',
            backgroundColor: '#3b82f6',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            cursor: isLoading ? 'not-allowed' : 'pointer',
            opacity: isLoading ? 0.6 : 1
          }}
        >
          {isLoading ? '🔄 Running...' : '🧪 Run Self-Test'}
        </button>

        <button
          onClick={handleSelfRepair}
          disabled={isLoading}
          style={{
            padding: '10px 20px',
            backgroundColor: '#10b981',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            cursor: isLoading ? 'not-allowed' : 'pointer',
            opacity: isLoading ? 0.6 : 1
          }}
        >
          {isLoading ? '🔄 Repairing...' : '🔧 Run Self-Repair'}
        </button>

        <button
          onClick={() => window.location.reload()}
          style={{
            padding: '10px 20px',
            backgroundColor: '#6b7280',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer'
          }}
        >
          🔄 Refresh
        </button>
      </div>

      {/* Self-Test Results */}
      {selfTestResult && (
        <div style={{ 
          padding: '15px', 
          backgroundColor: '#2a2a2a', 
          borderRadius: '6px', 
          border: `2px solid ${getStatusColor(selfTestResult.status)}`,
          marginTop: '20px'
        }}>
          <h3 style={{ 
            color: getStatusColor(selfTestResult.status), 
            margin: '0 0 10px 0' 
          }}>
            📋 Test Results
          </h3>
          <div><strong>Status:</strong> {selfTestResult.status}</div>
          <div><strong>Message:</strong> {selfTestResult.message}</div>
          
          {selfTestResult.tests && (
            <div style={{ marginTop: '10px' }}>
              <strong>Test Details:</strong>
              {Object.entries(selfTestResult.tests).map(([key, value]) => (
                <div key={key} style={{ 
                  marginLeft: '10px', 
                  fontSize: '12px',
                  marginTop: '5px'
                }}>
                  <span style={{ color: getStatusColor(value?.status) }}>●</span> {key}: {value?.status || 'unknown'}
                  {value?.response_time && ` (${value.response_time})`}
                </div>
              ))}
            </div>
          )}

          {selfTestResult.actions_taken && (
            <div style={{ marginTop: '10px' }}>
              <strong>Actions Taken:</strong>
              {selfTestResult.actions_taken.map((action, index) => (
                <div key={index} style={{ 
                  marginLeft: '10px', 
                  fontSize: '12px',
                  marginTop: '2px'
                }}>
                  • {action}
                </div>
              ))}
            </div>
          )}

          {selfTestResult.error && (
            <div style={{ 
              marginTop: '10px', 
              padding: '8px', 
              backgroundColor: '#ef4444', 
              borderRadius: '4px', 
              fontSize: '12px' 
            }}>
              <strong>Error:</strong> {selfTestResult.error}
            </div>
          )}

          <div style={{ 
            fontSize: '12px', 
            color: '#888', 
            marginTop: '10px' 
          }}>
            {formatTimestamp(selfTestResult.timestamp)}
          </div>
        </div>
      )}
    </div>
  );
};

export default SystemSelfTest;