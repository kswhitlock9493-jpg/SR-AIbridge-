import React, { useState, useEffect } from 'react';
import { 
  getStatus, 
  getAgents, 
  getMissions, 
  getVaultLogs, 
  getArmadaStatus, 
  getSystemHealth,
  getActivity 
} from '../api';

const Dashboard = () => {
  const [status, setStatus] = useState({
    agentsOnline: 0,
    activeMissions: 0,
    admiral: "Loading..."
  });
  const [agents, setAgents] = useState([]);
  const [missions, setMissions] = useState([]);
  const [vaultLogs, setVaultLogs] = useState([]);
  const [armadaStatus, setArmadaStatus] = useState({});
  const [systemHealth, setSystemHealth] = useState({});
  const [activity, setActivity] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(new Date());

  // Fetch all dashboard data
  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [
        statusData,
        agentsData,
        missionsData,
        vaultData,
        armadaData,
        healthData,
        activityData
      ] = await Promise.allSettled([
        getStatus(),
        getAgents(),
        getMissions(),
        getVaultLogs(),
        getArmadaStatus(),
        getSystemHealth(),
        getActivity()
      ]);

      // Process results with error handling
      if (statusData.status === 'fulfilled') {
        setStatus(statusData.value);
      }
      if (agentsData.status === 'fulfilled') {
        setAgents(Array.isArray(agentsData.value) ? agentsData.value : []);
      }
      if (missionsData.status === 'fulfilled') {
        setMissions(Array.isArray(missionsData.value) ? missionsData.value : []);
      }
      if (vaultData.status === 'fulfilled') {
        setVaultLogs(Array.isArray(vaultData.value) ? vaultData.value : []);
      }
      if (armadaData.status === 'fulfilled') {
        setArmadaStatus(armadaData.value || {});
      }
      if (healthData.status === 'fulfilled') {
        setSystemHealth(healthData.value || {});
      }
      if (activityData.status === 'fulfilled') {
        setActivity(Array.isArray(activityData.value) ? activityData.value : []);
      }

      setLastUpdate(new Date());
    } catch (err) {
      console.error('Dashboard data fetch error:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Initial load and periodic refresh
  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  // Helper functions for data processing
  const getOnlineAgents = () => {
    return agents.filter(agent => agent.status === 'online' || agent.status === 'active').length;
  };

  const getActiveMissions = () => {
    return missions.filter(mission => mission.status === 'active' || mission.status === 'in_progress').length;
  };

  const getSystemStatus = () => {
    if (systemHealth.status === 'healthy') return 'Operational';
    if (systemHealth.status === 'degraded') return 'Degraded';
    if (systemHealth.status === 'unhealthy') return 'Critical';
    return 'Unknown';
  };

  const getStatusColor = () => {
    if (systemHealth.status === 'healthy') return '#28a745';
    if (systemHealth.status === 'degraded') return '#ffc107';
    return '#dc3545';
  };

  if (loading && !status.admiral) {
    return (
      <div className="dashboard loading">
        <div className="loading-spinner">
          <span>⏳</span>
          <p>Loading Dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h2>🌉 SR-AIbridge Command Dashboard</h2>
        <div className="last-update">
          Last Updated: {lastUpdate.toLocaleTimeString()}
          <button onClick={fetchDashboardData} className="refresh-btn">
            🔄 Refresh
          </button>
        </div>
      </div>

      {error && (
        <div className="error-banner">
          <span>⚠️</span>
          <span>Error: {error}</span>
          <button onClick={fetchDashboardData}>Retry</button>
        </div>
      )}

      <div className="dashboard-grid">
        {/* System Status Panel */}
        <div className="status-panel">
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
              <span className="metric-value">{getOnlineAgents()}/{agents.length}</span>
            </div>
            <div className="metric">
              <span className="metric-label">Active Missions:</span>
              <span className="metric-value">{getActiveMissions()}</span>
            </div>
            <div className="metric">
              <span className="metric-label">Admiral:</span>
              <span className="metric-value">{status.admiral || 'Unknown'}</span>
            </div>
            <div className="metric">
              <span className="metric-label">Vault Entries:</span>
              <span className="metric-value">{vaultLogs.length}</span>
            </div>
          </div>
        </div>

        {/* Recent Activity Panel */}
        <div className="activity-panel">
          <div className="panel-header">
            <h3>📊 Recent Activity</h3>
          </div>
          <div className="activity-list">
            {activity.length > 0 ? (
              activity.slice(0, 5).map((item, index) => (
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
        <div className="agents-panel">
          <div className="panel-header">
            <h3>👥 Agents Overview</h3>
          </div>
          <div className="agents-grid">
            {agents.length > 0 ? (
              agents.slice(0, 6).map((agent) => (
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
        <div className="missions-panel">
          <div className="panel-header">
            <h3>🚀 Mission Status</h3>
          </div>
          <div className="missions-list">
            {missions.length > 0 ? (
              missions.slice(0, 4).map((mission) => (
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
        <div className="armada-panel">
          <div className="panel-header">
            <h3>🗺️ Armada Status</h3>
          </div>
          <div className="armada-info">
            <div className="armada-metric">
              <span>Fleet Size:</span>
              <span>{armadaStatus.fleetSize || 0}</span>
            </div>
            <div className="armada-metric">
              <span>Active Ships:</span>
              <span>{armadaStatus.activeShips || 0}</span>
            </div>
            <div className="armada-metric">
              <span>Fleet Status:</span>
              <span>{armadaStatus.status || 'Standby'}</span>
            </div>
          </div>
        </div>

        {/* Quick Actions Panel */}
        <div className="actions-panel">
          <div className="panel-header">
            <h3>⚡ Quick Actions</h3>
          </div>
          <div className="action-buttons">
            <button className="action-btn refresh" onClick={fetchDashboardData}>
              🔄 Refresh All
            </button>
            <button className="action-btn health" onClick={() => window.location.hash = '#health'}>
              🏥 System Health
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;