import React, { useState } from 'react';
import { getVaultLogs } from '../api';
import { usePolling } from '../hooks/usePolling';

const VaultLogs = () => {
  const [logs, setLogs] = useState([]);

  /**
   * Optimized data fetching function for vault logs
   * Implements efficient state management for log data
   */
  const fetchLogs = async () => {
    const data = await getVaultLogs();
    setLogs(data);
    return data;
  };

  /**
   * Use optimized polling with 10-second intervals for vault logs  
   * Vault logs require more frequent updates to show live activity
   * Includes debounced loading states for smoother UX
   */
  const { loading, error, refresh } = usePolling(fetchLogs, {
    interval: 10000, // 10 seconds - high frequency for live log monitoring
    immediate: true,
    debounceDelay: 200
  });

  // Utility functions for log formatting
  const getLevelColor = (level) => {
    switch (level?.toLowerCase()) {
      case 'error': return '#ff4444';
      case 'warning': return '#ffaa00';
      case 'info': return '#00aaff';
      default: return '#888';
    }
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  if (loading) {
    return (
      <div className="vault-logs">
        <h2>📜 Vault Logs</h2>
        <div className="loading">Loading vault logs...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="vault-logs">
        <h2>📜 Vault Logs</h2>
        <div className="error">Error loading logs: {error}</div>
        <button onClick={refresh} className="retry-button">Retry</button>
      </div>
    );
  }

  return (
    <div className="vault-logs">
      <div className="header">
        <h2>📜 Vault Logs</h2>
        {/* Manual refresh button for immediate log updates when needed */}
        <button onClick={refresh} className="refresh-button">🔄 Refresh</button>
      </div>
      
      <div className="logs-container">
        {logs.length === 0 ? (
          <div className="no-logs">No vault logs available</div>
        ) : (
          <div className="logs-list">
            {logs.map((log) => (
              <div key={log.id} className="log-entry">
                <div className="log-header">
                  <span className="agent-name">{log.agent_name}</span>
                  <span 
                    className="log-level" 
                    style={{ color: getLevelColor(log.log_level) }}
                  >
                    {log.log_level?.toUpperCase()}
                  </span>
                  <span className="timestamp">{formatTimestamp(log.timestamp)}</span>
                </div>
                <div className="log-action">{log.action}</div>
                <div className="log-details">{log.details}</div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default VaultLogs;