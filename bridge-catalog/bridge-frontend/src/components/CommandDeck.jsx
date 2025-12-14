import { useState, useEffect, useCallback } from 'react';
import { 
  getStatus, 
  getAgents, 
  getMissions, 
  getVaultLogs, 
  getArmadaStatus, 
  getSystemHealth,
  getActivity 
} from '../api';
import config from '../config';
import UnifiedLeviathanPanel from './leviathan/UnifiedLeviathanPanel';
import '../styles/command-deck.css';

const API_BASE_URL = config.API_BASE_URL;

// Command Deck - Enhanced Dashboard with better error handling and UX
const CommandDeck = () => {
  // Core state management
  const [dashboardState, setDashboardState] = useState({
    status: { agentsOnline: 0, activeMissions: 0, admiral: "Loading..." },
    agents: [],
    missions: [],
    vaultLogs: [],
    armadaStatus: {},
    systemHealth: {},
    activity: [],
    loading: true,
    error: null,
    lastUpdate: new Date(),
    connectionStatus: 'connecting'
  });

  // Memoized data processing functions
  const getOnlineAgents = useCallback(() => {
    return dashboardState.agents.filter(agent => 
      agent.status === 'online' || agent.status === 'active'
    ).length;
  }, [dashboardState.agents]);

  const getActiveMissions = useCallback(() => {
    return dashboardState.missions.filter(mission => 
      mission.status === 'active' || mission.status === 'in_progress'
    ).length;
  }, [dashboardState.missions]);

  const getSystemStatus = useCallback(() => {
    const health = dashboardState.systemHealth.status;
    if (health === 'healthy') return 'Operational';
    if (health === 'degraded') return 'Degraded';
    if (health === 'unhealthy') return 'Critical';
    return 'Unknown';
  }, [dashboardState.systemHealth]);

  const getStatusColor = useCallback(() => {
    const health = dashboardState.systemHealth.status;
    if (health === 'healthy') return '#28a745';
    if (health === 'degraded') return '#ffc107';
    return '#dc3545';
  }, [dashboardState.systemHealth]);

  // Enhanced data fetching with better error handling
  const fetchCommandDeckData = useCallback(async () => {
    try {
      setDashboardState(prev => ({ 
        ...prev, 
        loading: true, 
        error: null, 
        connectionStatus: 'connecting' 
      }));

      const dataFetchers = [
        getStatus,     // index 0 - critical
        getAgents,     // index 1 - critical
        getMissions,   // index 2 - critical
        getVaultLogs,
        getArmadaStatus,
        getSystemHealth,
        getActivity
      ];

      // Define critical endpoint indices
      const CRITICAL_ENDPOINTS = [0, 1, 2]; // status, agents, missions

      const results = await Promise.allSettled(dataFetchers.map(fetcher => fetcher()));
      
      const [
        statusResult,
        agentsResult,
        missionsResult,
        vaultResult,
        armadaResult,
        healthResult,
        activityResult
      ] = results;

      // Process results with enhanced error handling
      const updates = {
        loading: false,
        lastUpdate: new Date(),
        connectionStatus: 'connected'
      };

      if (statusResult.status === 'fulfilled') {
        updates.status = statusResult.value;
      }
      if (agentsResult.status === 'fulfilled') {
        const agentsData = agentsResult.value;
        updates.agents = Array.isArray(agentsData) ? agentsData : 
                        (agentsData?.agents ? agentsData.agents : []);
      }
      if (missionsResult.status === 'fulfilled') {
        const missionsData = missionsResult.value;
        updates.missions = Array.isArray(missionsData) ? missionsData : 
                          (missionsData?.missions ? missionsData.missions : []);
      }
      if (vaultResult.status === 'fulfilled') {
        const vaultData = vaultResult.value;
        updates.vaultLogs = Array.isArray(vaultData) ? vaultData : 
                           (vaultData?.logs ? vaultData.logs : []);
      }
      if (armadaResult.status === 'fulfilled') {
        updates.armadaStatus = armadaResult.value || {};
      }
      if (healthResult.status === 'fulfilled') {
        updates.systemHealth = healthResult.value || {};
      }
      if (activityResult.status === 'fulfilled') {
        const activityData = activityResult.value;
        updates.activity = Array.isArray(activityData) ? activityData : 
                          (activityData?.activity ? activityData.activity : []);
      }

      // Check if any critical endpoints failed
      const criticalFailures = results.filter((result, index) => 
        result.status === 'rejected' && CRITICAL_ENDPOINTS.includes(index)
      );

      if (criticalFailures.length > 0) {
        updates.error = `${criticalFailures.length} critical endpoint(s) failed`;
        // If ALL critical endpoints failed, it's a connection issue
        if (criticalFailures.length === CRITICAL_ENDPOINTS.length) {
          updates.connectionStatus = 'failed';
        } else {
          updates.connectionStatus = 'degraded';
        }
      }

      setDashboardState(prev => ({ ...prev, ...updates }));

    } catch (err) {
      console.error('Command Deck data fetch error:', err);
      setDashboardState(prev => ({ 
        ...prev, 
        loading: false,
        error: err.message,
        connectionStatus: 'failed'
      }));
    }
  }, []);

  // Auto-refresh with cleanup
  useEffect(() => {
    fetchCommandDeckData();
    const interval = setInterval(fetchCommandDeckData, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, [fetchCommandDeckData]);

  // Connection status indicator
  const ConnectionStatus = () => (
    <div className={`connection-status ${dashboardState.connectionStatus}`}>
      <span className="status-dot"></span>
      <span className="status-text">
        {dashboardState.connectionStatus === 'connected' && 'Online'}
        {dashboardState.connectionStatus === 'connecting' && 'Connecting...'}
        {dashboardState.connectionStatus === 'degraded' && 'Degraded'}
        {dashboardState.connectionStatus === 'failed' && 'Offline'}
      </span>
    </div>
  );

  // Loading state - only show spinner on initial load
  if (dashboardState.loading && dashboardState.connectionStatus === 'connecting') {
    return (
      <div className="command-deck loading">
        <div className="loading-spinner">
          <div className="spinner-ring"></div>
          <p>Initializing Command Deck...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="command-deck">
      {/* Enhanced Header */}
      <div className="command-deck-header">
        <div className="header-title">
          <h2>🌉 SR-AIbridge Command Deck</h2>
          <ConnectionStatus />
        </div>
        <div className="header-controls">
          <div className="last-update">
            Last Updated: {dashboardState.lastUpdate.toLocaleTimeString()}
          </div>
          <button 
            onClick={fetchCommandDeckData} 
            className="refresh-btn"
            disabled={dashboardState.loading}
          >
            {dashboardState.loading ? '⏳' : '🔄'} Refresh
          </button>
        </div>
      </div>

      {/* Backend Connection Error Banner */}
      {(dashboardState.connectionStatus === 'failed' || dashboardState.connectionStatus === 'degraded') && (
        <div className="error-banner backend-config-notice">
          <div className="error-content">
            <span className="error-icon">🔌</span>
            <div className="error-message">
              <strong>Backend Connection Failed</strong>
              <p>Cannot connect to BRH (Bridge Runtime Handler) backend at <code>{API_BASE_URL}</code></p>
              <details className="config-details">
                <summary>Configuration Help</summary>
                <div className="config-help">
                  <p><strong>To configure the backend:</strong></p>
                  <ol>
                    <li>Start BRH: <code>python -m brh.run</code> (default port: 8000)</li>
                    <li>Or set <code>VITE_API_BASE</code> environment variable to your backend URL</li>
                    <li>For Netlify deployment, configure backend URL in build settings</li>
                  </ol>
                  <p><strong>Current API Base:</strong> <code>{API_BASE_URL}</code></p>
                </div>
              </details>
            </div>
          </div>
          <button onClick={fetchCommandDeckData} className="retry-btn">
            Retry Connection
          </button>
        </div>
      )}

      {/* Error Banner */}
      {dashboardState.error && dashboardState.connectionStatus === 'connected' && (
        <div className="error-banner">
          <span className="error-icon">⚠️</span>
          <span className="error-message">Error: {dashboardState.error}</span>
          <button onClick={fetchCommandDeckData} className="retry-btn">
            Retry
          </button>
        </div>
      )}

      {/* Main Command Grid */}
      <div className="command-grid">
        {/* System Status Panel */}
        <div className="panel status-panel">
          <div className="panel-header">
            <h3>🛰️ System Status</h3>
            <div 
              className="status-indicator"
              style={{ backgroundColor: getStatusColor() }}
            >
              {getSystemStatus()}
            </div>
          </div>
          <div className="status-metrics">
            <div className="metric">
              <span className="metric-label">Agents Online:</span>
              <span className="metric-value">
                {getOnlineAgents()}/{dashboardState.agents.length}
              </span>
            </div>
            <div className="metric">
              <span className="metric-label">Active Missions:</span>
              <span className="metric-value">{getActiveMissions()}</span>
            </div>
            <div className="metric">
              <span className="metric-label">Admiral:</span>
              <span className="metric-value">
                {dashboardState.status.admiral || 'Unknown'}
              </span>
            </div>
            <div className="metric">
              <span className="metric-label">Vault Entries:</span>
              <span className="metric-value">{dashboardState.vaultLogs.length}</span>
            </div>
          </div>
        </div>

        {/* Recent Activity Panel */}
        <div className="panel activity-panel">
          <div className="panel-header">
            <h3>📊 Recent Activity</h3>
          </div>
          <div className="activity-list">
            {dashboardState.activity.length > 0 ? (
              dashboardState.activity.slice(0, 5).map((item, index) => (
                <div key={index} className="activity-item">
                  <span className="activity-time">
                    {new Date(item.timestamp || Date.now()).toLocaleTimeString()}
                  </span>
                  <span className="activity-description">
                    {item.action || item.description || item.message || 'Activity logged'}
                  </span>
                </div>
              ))
            ) : (
              <div className="no-activity">No recent activity</div>
            )}
          </div>
        </div>

        {/* Agents Overview Panel */}
        <div className="panel agents-panel">
          <div className="panel-header">
            <h3>👥 Agents Overview</h3>
          </div>
          <div className="agents-grid">
            {dashboardState.agents.length > 0 ? (
              dashboardState.agents.slice(0, 6).map((agent) => (
                <div key={agent.id} className={`agent-card ${agent.status || 'offline'}`}>
                  <div className="agent-name">{agent.name || `Agent ${agent.id}`}</div>
                  <div className="agent-status">{agent.status || 'offline'}</div>
                  <div className="agent-type">{agent.type || 'Standard'}</div>
                </div>
              ))
            ) : (
              <div className="no-agents">No agents registered</div>
            )}
          </div>
        </div>

        {/* Mission Status Panel */}
        <div className="panel missions-panel">
          <div className="panel-header">
            <h3>🚀 Mission Status</h3>
          </div>
          <div className="missions-list">
            {dashboardState.missions.length > 0 ? (
              dashboardState.missions.slice(0, 4).map((mission) => (
                <div key={mission.id} className={`mission-item ${mission.status || 'pending'}`}>
                  <div className="mission-title">
                    {mission.title || mission.name || `Mission ${mission.id}`}
                  </div>
                  <div className="mission-status">{mission.status || 'pending'}</div>
                  <div className="mission-progress">
                    {mission.progress ? `${mission.progress}%` : 'N/A'}
                  </div>
                </div>
              ))
            ) : (
              <div className="no-missions">No active missions</div>
            )}
          </div>
        </div>

        {/* Armada Status Panel */}
        <div className="panel armada-panel">
          <div className="panel-header">
            <h3>🗺️ Armada Status</h3>
          </div>
          <div className="armada-info">
            <div className="armada-metric">
              <span>Fleet Size:</span>
              <span>{dashboardState.armadaStatus.fleetSize || 0}</span>
            </div>
            <div className="armada-metric">
              <span>Active Ships:</span>
              <span>{dashboardState.armadaStatus.activeShips || 0}</span>
            </div>
            <div className="armada-metric">
              <span>Fleet Status:</span>
              <span>{dashboardState.armadaStatus.status || 'Standby'}</span>
            </div>
          </div>
        </div>

        {/* Quick Actions Panel */}
        <div className="panel actions-panel">
          <div className="panel-header">
            <h3>⚡ Quick Actions</h3>
          </div>
          <div className="action-buttons">
            <button className="action-btn refresh" onClick={fetchCommandDeckData}>
              🔄 Refresh All
            </button>
            <button 
              className="action-btn health" 
              onClick={() => window.location.hash = '#health'}
            >
              🏥 System Health
            </button>
            <button 
              className="action-btn missions" 
              onClick={() => window.location.hash = '#missions'}
            >
              🚀 Missions
            </button>
          </div>
        </div>
      </div>

      {/* Leviathan Unified Search Panel */}
      <div style={{ marginTop: 16 }}>
        <UnifiedLeviathanPanel />
      </div>
    </div>
  );
};

export default CommandDeck;