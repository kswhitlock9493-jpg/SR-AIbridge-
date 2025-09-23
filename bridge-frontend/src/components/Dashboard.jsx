import React, { useState, useEffect } from 'react';
import { getStatus, getAgents, getMissions, getVaultLogs, getArmadaStatus } from '../api';

const Dashboard = () => {
  const [status, setStatus] = useState({});
  const [agents, setAgents] = useState([]);
  const [missions, setMissions] = useState([]);
  const [logs, setLogs] = useState([]);
  const [fleet, setFleet] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchAllData();
    const interval = setInterval(fetchAllData, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchAllData = async () => {
    try {
      setLoading(true);
      const [statusData, agentsData, missionsData, logsData, fleetData] = await Promise.all([
        getStatus(),
        getAgents(),
        getMissions(),
        getVaultLogs(),
        getArmadaStatus()
      ]);
      
      setStatus(statusData);
      setAgents(agentsData);
      setMissions(missionsData);
      setLogs(logsData);
      setFleet(fleetData);
      setError(null);
    } catch (err) {
      setError(err.message);
      console.error('Failed to fetch dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

  const getOnlineAgents = () => agents.filter(a => a.status === 'online').length;
  const getActiveMissions = () => missions.filter(m => m.status === 'active').length;
  const getOnlineShips = () => fleet.filter(s => s.status === 'online').length;
  const getRecentLogs = () => logs.slice(0, 5);

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
        <button onClick={fetchAllData} className="retry-button">Retry</button>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <div className="header">
        <h2>📊 Bridge Dashboard</h2>
        <button onClick={fetchAllData} className="refresh-button">🔄 Refresh</button>
      </div>

      <div className="dashboard-grid">
        {/* Status Overview */}
        <div className="dashboard-card status-overview">
          <h3>🎯 System Status</h3>
          <div className="status-grid">
            <div className="status-item">
              <span className="label">Admiral:</span>
              <span className="value">{status.admiral}</span>
            </div>
            <div className="status-item">
              <span className="label">Agents Online:</span>
              <span className="value online">{getOnlineAgents()}/{agents.length}</span>
            </div>
            <div className="status-item">
              <span className="label">Active Missions:</span>
              <span className="value active">{getActiveMissions()}</span>
            </div>
            <div className="status-item">
              <span className="label">Fleet Online:</span>
              <span className="value online">{getOnlineShips()}/{fleet.length}</span>
            </div>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="dashboard-card recent-activity">
          <h3>⚡ Recent Activity</h3>
          <div className="activity-list">
            {getRecentLogs().map((log) => (
              <div key={log.id} className="activity-item">
                <span className="agent">{log.agent_name}:</span>
                <span className="action">{log.action}</span>
                <span className="time">{new Date(log.timestamp).toLocaleTimeString()}</span>
              </div>
            ))}
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
            {fleet.slice(0, 4).map((ship) => (
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