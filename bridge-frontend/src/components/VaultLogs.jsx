import React, { useState, useEffect } from 'react';
import { useBridge } from '../hooks/useBridge';

const VaultLogs = () => {
  const { 
    vaultLogs: logs, 
    realTimeData, 
    loading, 
    error, 
    refreshData 
  } = useBridge();
  
  const [filteredLogs, setFilteredLogs] = useState([]);

  /**
   * Update filtered logs with real-time data
   */
  useEffect(() => {
    const realTimeLogs = realTimeData.vaultLogs || [];
    // Real-time updates are already managed by the bridge context
    if (realTimeLogs.length > 0) {
      console.log('📡 Real-time vault logs available:', realTimeLogs.length);
    }
    
    // Set filtered logs to all logs for now (can add filtering later)
    setFilteredLogs(logs);
  }, [logs, realTimeData.vaultLogs]);

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

  if (loading && filteredLogs.length === 0) {
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
        <button onClick={() => refreshData('vault')} className="retry-button">🔄 Reconnect</button>
      </div>
    );
  }

  return (
    <div className="vault-logs">
      <div className="header">
        <h2>📜 Vault Logs</h2>
        <div className="header-info">
          <span className="live-indicator">🔴 LIVE</span>
          <button onClick={() => refreshData('vault')} className="refresh-button">🔄 Refresh</button>
        </div>
      </div>
      
      <div className="logs-container">
        {filteredLogs.length === 0 ? (
          <div className="no-logs">
            <div className="placeholder-icon">📡</div>
            <div>Waiting for vault logs...</div>
            <div className="subtitle">Real-time log streaming is active</div>
          </div>
        ) : (
          <div className="logs-list">
            {filteredLogs.map((log, index) => (
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
          Total logs: {filteredLogs.length} | Real-time updates: Active
        </div>
      </div>
    </div>
  );
};

export default VaultLogs;