/**
 * VaultManager Component
 * Secure storage and log management interface
 */

import { useState } from 'react';
import { useRealtimeData } from '../hooks/useBRHConnection';

const VaultManager = () => {
  const [logLevel, setLogLevel] = useState('all');
  const [limit, setLimit] = useState(50);

  const { data: logs, loading, error, refetch } = useRealtimeData('vault/logs', {
    refreshInterval: 15000, // Update every 15 seconds
  });

  // Filter logs by level
  const filteredLogs = logs ? logs.filter(log => {
    if (logLevel === 'all') return true;
    return log.level === logLevel;
  }) : [];

  // Get log level color
  const getLogLevelColor = (level) => {
    switch (level?.toLowerCase()) {
      case 'critical':
      case 'error':
        return '#dc3545';
      case 'warning':
        return '#ffc107';
      case 'info':
        return '#17a2b8';
      case 'debug':
        return '#6c757d';
      default:
        return '#28a745';
    }
  };

  // Get log level icon
  const getLogLevelIcon = (level) => {
    switch (level?.toLowerCase()) {
      case 'critical':
        return '🔴';
      case 'error':
        return '❌';
      case 'warning':
        return '⚠️';
      case 'info':
        return 'ℹ️';
      case 'debug':
        return '🔍';
      default:
        return '📝';
    }
  };

  // Stats
  const totalLogs = logs ? logs.length : 0;
  const criticalCount = logs ? logs.filter(l => l.level === 'critical').length : 0;
  const errorCount = logs ? logs.filter(l => l.level === 'error').length : 0;
  const warningCount = logs ? logs.filter(l => l.level === 'warning').length : 0;

  return (
    <div className="vault-manager-panel panel">
      <div className="panel-header">
        <h3>📜 Vault Manager</h3>
        <button onClick={refetch} className="refresh-btn-small" disabled={loading}>
          {loading ? '⏳' : '🔄'} Refresh
        </button>
      </div>

      {error && (
        <div className="error-message">
          <span className="error-icon">⚠️</span>
          <span>Failed to load vault logs: {error}</span>
        </div>
      )}

      {/* Stats Summary */}
      <div className="vault-stats">
        <div className="stat-card total">
          <div className="stat-icon">📊</div>
          <div className="stat-info">
            <div className="stat-label">Total Logs</div>
            <div className="stat-value">{totalLogs}</div>
          </div>
        </div>
        <div className="stat-card critical">
          <div className="stat-icon">🔴</div>
          <div className="stat-info">
            <div className="stat-label">Critical</div>
            <div className="stat-value">{criticalCount}</div>
          </div>
        </div>
        <div className="stat-card error">
          <div className="stat-icon">❌</div>
          <div className="stat-info">
            <div className="stat-label">Errors</div>
            <div className="stat-value">{errorCount}</div>
          </div>
        </div>
        <div className="stat-card warning">
          <div className="stat-icon">⚠️</div>
          <div className="stat-info">
            <div className="stat-label">Warnings</div>
            <div className="stat-value">{warningCount}</div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="vault-filters">
        <div className="filter-group">
          <label htmlFor="log-level">Log Level:</label>
          <select
            id="log-level"
            value={logLevel}
            onChange={(e) => setLogLevel(e.target.value)}
            className="filter-select"
          >
            <option value="all">All Levels</option>
            <option value="critical">Critical</option>
            <option value="error">Error</option>
            <option value="warning">Warning</option>
            <option value="info">Info</option>
            <option value="debug">Debug</option>
          </select>
        </div>

        <div className="filter-group">
          <label htmlFor="log-limit">Display:</label>
          <select
            id="log-limit"
            value={limit}
            onChange={(e) => setLimit(parseInt(e.target.value))}
            className="filter-select"
          >
            <option value="25">Last 25</option>
            <option value="50">Last 50</option>
            <option value="100">Last 100</option>
            <option value="500">Last 500</option>
          </select>
        </div>
      </div>

      {/* Logs List */}
      <div className="vault-logs-list">
        {loading && !logs && (
          <div className="loading-message">Loading vault logs...</div>
        )}

        {!loading && filteredLogs.length === 0 && (
          <div className="no-data">No logs found</div>
        )}

        {filteredLogs.slice(0, limit).map((log, idx) => (
          <div
            key={idx}
            className="log-entry"
            style={{ borderLeftColor: getLogLevelColor(log.level) }}
          >
            <div className="log-header">
              <div className="log-level">
                <span className="level-icon">{getLogLevelIcon(log.level)}</span>
                <span
                  className="level-text"
                  style={{ color: getLogLevelColor(log.level) }}
                >
                  {log.level?.toUpperCase() || 'INFO'}
                </span>
              </div>
              <div className="log-timestamp">
                {log.timestamp
                  ? new Date(log.timestamp).toLocaleString()
                  : log.created_at
                  ? new Date(log.created_at).toLocaleString()
                  : 'Unknown'}
              </div>
            </div>

            <div className="log-message">
              {log.message || 'No message'}
            </div>

            {log.source && (
              <div className="log-source">
                <span className="source-label">Source:</span>
                <span className="source-value">{log.source}</span>
              </div>
            )}

            {log.metadata && Object.keys(log.metadata).length > 0 && (
              <details className="log-metadata">
                <summary>Metadata</summary>
                <pre>{JSON.stringify(log.metadata, null, 2)}</pre>
              </details>
            )}
          </div>
        ))}
      </div>

      {/* Export Options */}
      <div className="vault-actions">
        <button
          className="action-btn export"
          onClick={() => {
            const dataStr = JSON.stringify(filteredLogs, null, 2);
            const dataBlob = new Blob([dataStr], { type: 'application/json' });
            const url = URL.createObjectURL(dataBlob);
            const link = document.createElement('a');
            link.href = url;
            link.download = `vault-logs-${new Date().toISOString()}.json`;
            link.click();
            URL.revokeObjectURL(url);
          }}
          disabled={filteredLogs.length === 0}
        >
          📥 Export Logs
        </button>

        <button
          className="action-btn analyze"
          onClick={() => alert('Log analysis feature coming soon!')}
          disabled={filteredLogs.length === 0}
        >
          📊 Analyze Logs
        </button>
      </div>
    </div>
  );
};

export default VaultManager;
