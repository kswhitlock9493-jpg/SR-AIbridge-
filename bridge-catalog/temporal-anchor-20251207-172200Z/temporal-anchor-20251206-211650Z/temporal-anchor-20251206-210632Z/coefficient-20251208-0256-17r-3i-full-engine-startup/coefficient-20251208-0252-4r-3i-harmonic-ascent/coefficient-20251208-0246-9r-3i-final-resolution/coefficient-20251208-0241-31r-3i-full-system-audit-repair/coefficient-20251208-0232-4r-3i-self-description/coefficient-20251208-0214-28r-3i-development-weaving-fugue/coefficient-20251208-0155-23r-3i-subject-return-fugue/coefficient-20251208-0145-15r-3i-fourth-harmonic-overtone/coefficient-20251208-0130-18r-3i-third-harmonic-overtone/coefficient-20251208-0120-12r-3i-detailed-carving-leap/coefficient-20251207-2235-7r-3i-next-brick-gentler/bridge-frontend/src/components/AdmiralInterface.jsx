/**
 * AdmiralInterface Component
 * Command center for admiral-level operations
 */

import { useState } from 'react';
import { useBRHConnection } from '../hooks/useBRHConnection';
import BRHService from '../services/brh-api';

const AdmiralInterface = () => {
  const { isConnected, data: connectionData, refresh } = useBRHConnection({
    refreshInterval: 30000,
  });

  const [commandInput, setCommandInput] = useState('');
  const [commandHistory, setCommandHistory] = useState([]);
  const [executing, setExecuting] = useState(false);

  // Predefined commands
  const quickCommands = [
    { label: 'System Health', command: 'health.check', icon: '🏥' },
    { label: 'Fleet Status', command: 'fleet.status', icon: '🚢' },
    { label: 'Mission Report', command: 'mission.report', icon: '📊' },
    { label: 'Vault Logs', command: 'vault.query', icon: '📜' },
    { label: 'Self-Heal', command: 'system.heal', icon: '🔧' },
    { label: 'Refresh All', command: 'bridge.refresh', icon: '🔄' },
  ];

  // Execute command
  const executeCommand = async (cmd) => {
    if (!cmd.trim()) return;

    setExecuting(true);
    const timestamp = new Date().toLocaleTimeString();

    try {
      let result;

      // Route commands to appropriate BRH service methods
      switch (cmd.toLowerCase()) {
        case 'health.check':
        case 'health':
          result = await BRHService.getFullHealth();
          break;

        case 'fleet.status':
        case 'fleet':
          result = await BRHService.getFleetStatus();
          break;

        case 'mission.report':
        case 'missions':
          result = await BRHService.getMissions();
          break;

        case 'vault.query':
        case 'vault':
          result = await BRHService.getVaultLogs();
          break;

        case 'system.heal':
        case 'heal':
          result = await BRHService.triggerSelfHeal();
          break;

        case 'bridge.refresh':
        case 'refresh':
          result = await refresh();
          break;

        default:
          // Generic command execution
          result = await BRHService.sendCommand(cmd);
      }

      setCommandHistory(prev => [
        ...prev,
        {
          command: cmd,
          result,
          timestamp,
          success: true,
        },
      ]);
    } catch (error) {
      setCommandHistory(prev => [
        ...prev,
        {
          command: cmd,
          result: { error: error.message },
          timestamp,
          success: false,
        },
      ]);
    } finally {
      setExecuting(false);
      setCommandInput('');
    }
  };

  // Handle quick command click
  const handleQuickCommand = (command) => {
    executeCommand(command);
  };

  // Handle command input
  const handleCommandSubmit = (e) => {
    e.preventDefault();
    executeCommand(commandInput);
  };

  // Clear history
  const clearHistory = () => {
    setCommandHistory([]);
  };

  return (
    <div className="admiral-interface-panel panel">
      <div className="panel-header">
        <h3>⭐ Admiral Command Interface</h3>
        <div className="connection-badge">
          <span className={`status-dot ${isConnected ? 'connected' : 'disconnected'}`}></span>
          <span className="status-text">
            {isConnected ? 'Connected to BRH' : 'Disconnected'}
          </span>
        </div>
      </div>

      {/* Bridge Status Summary */}
      {connectionData && (
        <div className="bridge-status-summary">
          <div className="summary-item">
            <span className="label">Bridge Status:</span>
            <span className="value">{connectionData.status || 'Unknown'}</span>
          </div>
          <div className="summary-item">
            <span className="label">Agents Online:</span>
            <span className="value">{connectionData.agents || 0}</span>
          </div>
          {connectionData.admiral && (
            <div className="summary-item">
              <span className="label">Admiral:</span>
              <span className="value">{connectionData.admiral}</span>
            </div>
          )}
        </div>
      )}

      {/* Quick Commands */}
      <div className="quick-commands">
        <h4>Quick Commands</h4>
        <div className="quick-commands-grid">
          {quickCommands.map((qc, idx) => (
            <button
              key={idx}
              className="quick-command-btn"
              onClick={() => handleQuickCommand(qc.command)}
              disabled={executing || !isConnected}
            >
              <span className="command-icon">{qc.icon}</span>
              <span className="command-label">{qc.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Command Input */}
      <div className="command-input-section">
        <h4>Execute Command</h4>
        <form onSubmit={handleCommandSubmit} className="command-form">
          <input
            type="text"
            value={commandInput}
            onChange={(e) => setCommandInput(e.target.value)}
            placeholder="Enter command (e.g., health.check, fleet.status)"
            className="command-input"
            disabled={executing || !isConnected}
          />
          <button
            type="submit"
            className="execute-btn"
            disabled={executing || !isConnected || !commandInput.trim()}
          >
            {executing ? '⏳ Executing...' : '▶ Execute'}
          </button>
        </form>
      </div>

      {/* Command History */}
      <div className="command-history">
        <div className="history-header">
          <h4>Command History</h4>
          {commandHistory.length > 0 && (
            <button onClick={clearHistory} className="clear-btn">
              Clear History
            </button>
          )}
        </div>

        {commandHistory.length === 0 ? (
          <div className="no-history">No commands executed yet</div>
        ) : (
          <div className="history-list">
            {[...commandHistory].reverse().map((entry, idx) => (
              <div key={idx} className={`history-entry ${entry.success ? 'success' : 'error'}`}>
                <div className="entry-header">
                  <span className="entry-icon">
                    {entry.success ? '✅' : '❌'}
                  </span>
                  <span className="entry-command">{entry.command}</span>
                  <span className="entry-timestamp">{entry.timestamp}</span>
                </div>
                <div className="entry-result">
                  <pre>{JSON.stringify(entry.result, null, 2)}</pre>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Help Text */}
      <div className="command-help">
        <details>
          <summary>Available Commands</summary>
          <div className="help-content">
            <ul>
              <li><code>health.check</code> - Get full system health status</li>
              <li><code>fleet.status</code> - Get fleet/agents status</li>
              <li><code>mission.report</code> - Get missions report</li>
              <li><code>vault.query</code> - Query vault logs</li>
              <li><code>system.heal</code> - Trigger self-heal operation</li>
              <li><code>bridge.refresh</code> - Refresh bridge connection</li>
            </ul>
          </div>
        </details>
      </div>
    </div>
  );
};

export default AdmiralInterface;
