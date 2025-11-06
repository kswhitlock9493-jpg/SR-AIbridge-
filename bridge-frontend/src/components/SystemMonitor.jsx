/**
 * SystemMonitor Component
 * Real-time endpoint health monitoring and system diagnostics
 */

import { useState, useEffect } from 'react';
import { useRealtimeData } from '../hooks/useBRHConnection';
import BRHService from '../services/brh-api';

const SystemMonitor = () => {
  const { data: healthData, loading, error, lastUpdate, refetch } = useRealtimeData('health/full', {
    refreshInterval: 10000, // Update every 10 seconds
  });

  const [selfHealLoading, setSelfHealLoading] = useState(false);
  const [selfHealResult, setSelfHealResult] = useState(null);

  // Parse health data
  const status = healthData?.status || 'unknown';
  const components = healthData?.components || {};
  const metrics = healthData?.metrics || {};

  // Determine overall health status
  const getStatusColor = (status) => {
    switch (status) {
      case 'healthy':
      case 'connected':
      case 'operational':
      case 'active':
        return '#28a745'; // Green
      case 'degraded':
      case 'warning':
        return '#ffc107'; // Yellow
      case 'unhealthy':
      case 'critical':
      case 'error':
        return '#dc3545'; // Red
      default:
        return '#6c757d'; // Gray
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'healthy':
      case 'connected':
      case 'operational':
      case 'active':
        return '✅';
      case 'degraded':
      case 'warning':
        return '⚠️';
      case 'unhealthy':
      case 'critical':
      case 'error':
        return '❌';
      default:
        return '❓';
    }
  };

  // Trigger self-heal
  const handleSelfHeal = async () => {
    setSelfHealLoading(true);
    setSelfHealResult(null);

    try {
      const result = await BRHService.triggerSelfHeal();
      setSelfHealResult(result);
      // Refetch health after heal
      setTimeout(() => {
        refetch();
      }, 2000);
    } catch (err) {
      setSelfHealResult({ success: false, error: err.message });
    } finally {
      setSelfHealLoading(false);
    }
  };

  return (
    <div className="system-monitor-panel panel">
      <div className="panel-header">
        <h3>🔍 System Monitor</h3>
        <div className="monitor-controls">
          <button
            onClick={refetch}
            className="refresh-btn-small"
            disabled={loading}
          >
            {loading ? '⏳' : '🔄'} Refresh
          </button>
          <button
            onClick={handleSelfHeal}
            className="heal-btn"
            disabled={selfHealLoading || status === 'healthy'}
          >
            {selfHealLoading ? '⏳' : '🔧'} Self-Heal
          </button>
        </div>
      </div>

      {error && (
        <div className="error-message">
          <span className="error-icon">⚠️</span>
          <span>Failed to load health data: {error}</span>
        </div>
      )}

      {selfHealResult && (
        <div className={`heal-result ${selfHealResult.success ? 'success' : 'error'}`}>
          <span className="result-icon">{selfHealResult.success ? '✅' : '❌'}</span>
          <span>
            {selfHealResult.success
              ? 'Self-heal completed successfully'
              : `Self-heal failed: ${selfHealResult.error}`}
          </span>
          <button onClick={() => setSelfHealResult(null)} className="close-btn">×</button>
        </div>
      )}

      {/* Overall Status */}
      <div className="overall-status">
        <div
          className="status-circle"
          style={{ backgroundColor: getStatusColor(status) }}
        >
          <span className="status-icon">{getStatusIcon(status)}</span>
        </div>
        <div className="status-details">
          <div className="status-label">System Status</div>
          <div className="status-value" style={{ color: getStatusColor(status) }}>
            {status.toUpperCase()}
          </div>
          {lastUpdate && (
            <div className="status-timestamp">
              Updated: {lastUpdate.toLocaleTimeString()}
            </div>
          )}
        </div>
      </div>

      {/* Component Health */}
      <div className="components-health">
        <h4>Component Health</h4>
        <div className="components-grid">
          {Object.entries(components).length > 0 ? (
            Object.entries(components).map(([name, componentStatus]) => (
              <div key={name} className="component-card">
                <div className="component-header">
                  <span className="component-name">{name}</span>
                  <span
                    className="component-status"
                    style={{ color: getStatusColor(componentStatus) }}
                  >
                    {getStatusIcon(componentStatus)} {componentStatus}
                  </span>
                </div>
              </div>
            ))
          ) : (
            <div className="no-data">No component data available</div>
          )}
        </div>
      </div>

      {/* System Metrics */}
      {Object.keys(metrics).length > 0 && (
        <div className="system-metrics">
          <h4>System Metrics</h4>
          <div className="metrics-grid">
            {Object.entries(metrics).map(([key, value]) => (
              <div key={key} className="metric-card">
                <div className="metric-label">{key.replace(/_/g, ' ')}</div>
                <div className="metric-value">
                  {typeof value === 'number' ? value.toLocaleString() : value}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Endpoint Status */}
      <div className="endpoints-status">
        <h4>Critical Endpoints</h4>
        <div className="endpoints-list">
          <div className="endpoint-item">
            <span className="endpoint-name">/health</span>
            <span className={`endpoint-status ${status !== 'unhealthy' ? 'online' : 'offline'}`}>
              {status !== 'unhealthy' ? '✅ Online' : '❌ Offline'}
            </span>
          </div>
          <div className="endpoint-item">
            <span className="endpoint-name">/status</span>
            <span className={`endpoint-status ${status !== 'unhealthy' ? 'online' : 'offline'}`}>
              {status !== 'unhealthy' ? '✅ Online' : '❌ Offline'}
            </span>
          </div>
          <div className="endpoint-item">
            <span className="endpoint-name">/agents</span>
            <span className={`endpoint-status ${components.database !== 'unhealthy' ? 'online' : 'offline'}`}>
              {components.database !== 'unhealthy' ? '✅ Online' : '❌ Offline'}
            </span>
          </div>
          <div className="endpoint-item">
            <span className="endpoint-name">/missions</span>
            <span className={`endpoint-status ${components.database !== 'unhealthy' ? 'online' : 'offline'}`}>
              {components.database !== 'unhealthy' ? '✅ Online' : '❌ Offline'}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SystemMonitor;
