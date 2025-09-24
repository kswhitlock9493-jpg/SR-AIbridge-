import React, { useState, useEffect } from 'react';
import { getVaultLogs } from '../api';

const VaultLogs = () => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchLogs();
    const interval = setInterval(fetchLogs, 5000); // Refresh every 5 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchLogs = async () => {
    try {
      setLoading(true);
      const data = await getVaultLogs();
      setLogs(data);
      setError(null);
    } catch (err) {
      setError(err.message);
      console.error('Failed to fetch vault logs:', err);
    } finally {
      setLoading(false);
    }
  };

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
        <button onClick={fetchLogs} className="retry-button">Retry</button>
      </div>
    );
  }

  return (
    <div className="vault-logs">
      <div className="header">
        <h2>📜 Vault Logs</h2>
        <button onClick={fetchLogs} className="refresh-button">🔄 Refresh</button>
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