import React from 'react';
import { useBridge } from '../hooks/useBridge';

const Dashboard = () => {
  const { 
    status, 
    agents, 
    missions, 
    vaultLogs: logs, 
    fleetData: fleet, 
    activity,
    loading, 
    error, 
    refreshData,
    fetchSystemHealth,
    systemHealth
  } = useBridge();

  // Helper functions for data processing with fallback handling
  const getOnlineAgents = () => {
    if (!Array.isArray(agents) || agents.length === 0) return 0;
    return agents.filter(a => a.status === 'online').length;
  };
  
  const getActiveMissions = () => {
    if (!Array.isArray(missions) || missions.length === 0) return 0;
    return missions.filter(m => m.status === 'active').length;
  };
  
  const getOnlineShips = () => {
    const fleetArray = fleet?.fleet || fleet || [];
    if (!Array.isArray(fleetArray) || fleetArray.length === 0) return 0;
    return fleetArray.filter(s => s.status === 'online').length;
  };
  
  const getFleetTotal = () => {
    const fleetArray = fleet?.fleet || fleet || [];
    return Array.isArray(fleetArray) ? fleetArray.length : 0;
  };
  
  const getRecentLogs = () => {
    // Use activity data if available, fallback to vault logs
    const activityData = activity && Array.isArray(activity) ? activity : [];
    const logsData = logs && Array.isArray(logs) ? logs : [];
    
    if (activityData.length > 0) {
      return activityData.slice(0, 5);
    }
    return logsData.slice(0, 5);
  };

  // Handle System Self-Test
  const handleSystemSelfTest = async () => {
    try {
      await fetchSystemHealth();
      // Show self-test results in system health state
    } catch (err) {
      console.error('Self-test failed:', err);
    }
  };

  if (loading) {
    return (
      <div className="dashboard">
        <h2>📊 Dashboard</h2>
        <div className="loading">Loading dashboard data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard">
        <h2>📊 Dashboard</h2>
        <div className="error">Error loading dashboard: {error}</div>
        <button onClick={() => refreshData()} className="retry-button">Retry</button>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <div className="header">
        <h2>📊 Bridge Dashboard</h2>
        {/* Manual refresh button for user-initiated updates */}
        <button onClick={() => refreshData()} className="refresh-button">🔄 Refresh</button>
      </div>

      <div className="dashboard-grid">
        {/* Status Overview */}
        <div className="dashboard-card status-overview">
          <h3>🎯 System Status</h3>
          <div className="status-grid">
            <div className="status-item">
              <span className="label">Admiral:</span>
              <span className="value">{status.admiral || "No Admiral"}</span>
            </div>
            <div className="status-item">
              <span className="label">Agents Online:</span>
              <span className="value online">
                {getOnlineAgents()}/{Array.isArray(agents) ? agents.length : 0}
                {agents.length === 0 && <span className="placeholder"> (No agents)</span>}
              </span>
            </div>
            <div className="status-item">
              <span className="label">Active Missions:</span>
              <span className="value active">
                {getActiveMissions()}
                {missions.length === 0 && <span className="placeholder"> (No missions)</span>}
              </span>
            </div>
            <div className="status-item">
              <span className="label">Fleet Online:</span>
              <span className="value online">
                {getOnlineShips()}/{getFleetTotal()}
                {getFleetTotal() === 0 && <span className="placeholder"> (No fleet data)</span>}
              </span>
            </div>
          </div>
          
          {/* System Self-Test Button */}
          <div className="self-test-section">
            <button onClick={handleSystemSelfTest} className="self-test-button">
              🔍 Run Self-Test
            </button>
            {systemHealth && (
              <div className={`system-health-status ${systemHealth.status}`}>
                Status: {systemHealth.status}
                {systemHealth.components && (
                  <div className="health-components">
                    {Object.entries(systemHealth.components).map(([component, data]) => (
                      <div key={component} className={`component-status ${data.status}`}>
                        {component}: {data.status}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Recent Activity */}
        <div className="dashboard-card recent-activity">
          <h3>⚡ Recent Activity</h3>
          <div className="activity-list">
            {getRecentLogs().length > 0 ? (
              getRecentLogs().map((item) => (
                <div key={item.id} className="activity-item">
                  <span className="agent">{item.agent_name || item.agent}:</span>
                  <span className="action">{item.action}</span>
                  <span className="time">{new Date(item.timestamp).toLocaleTimeString()}</span>
                </div>
              ))
            ) : (
              <div className="no-data">
                <span className="placeholder-text">No recent activity available</span>
              </div>
            )}
          </div>
        </div>

        {/* Mission Status */}
        <div className="dashboard-card mission-status">
          <h3>🚀 Mission Status</h3>
          <div className="mission-summary">
            {missions.slice(0, 3).map((mission) => (
              <div key={mission.id} className="mission-item">
                <div className="mission-title">{mission.title}</div>
                <div className="mission-status">
                  <span className={`status ${mission.status}`}>{mission.status}</span>
                  <span className={`priority ${mission.priority}`}>{mission.priority}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Fleet Status */}
        <div className="dashboard-card fleet-status">
          <h3>🗺️ Fleet Status</h3>
          <div className="fleet-summary">
            {(fleet?.fleet || fleet || []).slice(0, 4).map((ship) => (
              <div key={ship.id} className="fleet-item">
                <div className="ship-name">{ship.name}</div>
                <div className="ship-details">
                  <span className={`status ${ship.status}`}>● {ship.status}</span>
                  <span className="location">{ship.location}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;