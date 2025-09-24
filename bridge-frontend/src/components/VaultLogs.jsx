import React, { useState, useEffect } from 'react';
import { getVaultLogs } from '../api';
import { usePolling } from '../hooks/usePolling';

const VaultLogs = ({ realTimeLogs = [] }) => {
  const [logs, setLogs] = useState([]);

  /**
   * Enhanced data fetching that combines API data with real-time updates
   */
  const fetchLogs = async () => {
    const data = await getVaultLogs();
    setLogs(data);
    return data;
  };

  /**
   * Merge real-time logs with fetched logs, avoiding duplicates
   */
  useEffect(() => {
    if (realTimeLogs.length > 0) {
      setLogs(prevLogs => {
        const existingIds = new Set(prevLogs.map(log => log.id));
        const newLogs = realTimeLogs.filter(log => !existingIds.has(log.id));
        
        // Combine and sort by timestamp (newest first)
        const combined = [...newLogs, ...prevLogs]
          .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
          .slice(0, 100); // Keep only last 100 logs for performance
        
        return combined;
      });
    }
  }, [realTimeLogs]);

  /**
   * Use reduced polling frequency since we have real-time updates
   * Still poll periodically to ensure data consistency
   */
  const { loading, error, refresh } = usePolling(fetchLogs, {
    interval: 60000, // 60 seconds - reduced frequency due to real-time updates
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

  const getLogIcon = (action) => {
    switch (action?.toLowerCase()) {
      case 'mission_start': return '🚀';
      case 'mission_completed': return '✅';
      case 'mission_failed': return '❌';
      case 'mission_progress': return '⏳';
      case 'system_check': return '🔧';
      case 'alert': return '⚠️';
      case 'fleet_update': return '🚢';
      case 'data_analysis': return '📊';
      default: return '📝';
    }
  };

  if (loading && logs.length === 0) {
    return (
      <div className="vault-logs">
        <h2>📜 Vault Logs</h2>
        <div className="loading">Connecting to vault logs stream...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="vault-logs">
        <h2>📜 Vault Logs</h2>
        <div className="error">Error connecting to logs: {error}</div>
        <button onClick={refresh} className="retry-button">🔄 Reconnect</button>
      </div>
    );
  }

  return (
    <div className="vault-logs">
      <div className="header">
        <h2>📜 Vault Logs</h2>
        <div className="header-info">
          <span className="live-indicator">🔴 LIVE</span>
          <button onClick={refresh} className="refresh-button">🔄 Refresh</button>
        </div>
      </div>
      
      <div className="logs-container">
        {logs.length === 0 ? (
          <div className="no-logs">
            <div className="placeholder-icon">📡</div>
            <div>Waiting for vault logs...</div>
            <div className="subtitle">Real-time log streaming is active</div>
          </div>
        ) : (
          <div className="logs-list">
            {logs.map((log, index) => (
              <div 
                key={`${log.id}-${index}`} 
                className={`log-entry ${index < 3 ? 'recent' : ''}`}
              >
                <div className="log-header">
                  <span className="log-icon">{getLogIcon(log.action)}</span>
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
      
      <div className="logs-footer">
        <div className="status-info">
          Total logs: {logs.length} | Real-time updates: Active
        </div>
      </div>
    </div>
  );
};

export default VaultLogs;