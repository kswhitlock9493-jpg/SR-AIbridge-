import React, { useState, useEffect } from 'react';
import { getMissions } from '../api';

const MissionLog = () => {
  const [missions, setMissions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchMissions();
    const interval = setInterval(fetchMissions, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchMissions = async () => {
    try {
      setLoading(true);
      const data = await getMissions();
      setMissions(data);
      setError(null);
    } catch (err) {
      setError(err.message);
      console.error('Failed to fetch missions:', err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'active': return '#00ff00';
      case 'completed': return '#00aaff';
      case 'planning': return '#ffaa00';
      case 'failed': return '#ff4444';
      default: return '#888';
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority?.toLowerCase()) {
      case 'high': return '#ff4444';
      case 'medium': return '#ffaa00';
      case 'low': return '#00ff00';
      default: return '#888';
    }
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  if (loading) {
    return (
      <div className="mission-log">
        <h2>🚀 Mission Log</h2>
        <div className="loading">Loading missions...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="mission-log">
        <h2>🚀 Mission Log</h2>
        <div className="error">Error loading missions: {error}</div>
        <button onClick={fetchMissions} className="retry-button">Retry</button>
      </div>
    );
  }

  return (
    <div className="mission-log">
      <div className="header">
        <h2>🚀 Mission Log</h2>
        <button onClick={fetchMissions} className="refresh-button">🔄 Refresh</button>
      </div>
      
      <div className="missions-container">
        {missions.length === 0 ? (
          <div className="no-missions">No missions available</div>
        ) : (
          <div className="missions-list">
            {missions.map((mission) => (
              <div key={mission.id} className="mission-entry">
                <div className="mission-header">
                  <h3 className="mission-title">{mission.title}</h3>
                  <div className="mission-badges">
                    <span 
                      className="status-badge" 
                      style={{ color: getStatusColor(mission.status) }}
                    >
                      ● {mission.status?.toUpperCase()}
                    </span>
                    <span 
                      className="priority-badge" 
                      style={{ color: getPriorityColor(mission.priority) }}
                    >
                      {mission.priority?.toUpperCase()} PRIORITY
                    </span>
                  </div>
                </div>
                <div className="mission-description">{mission.description}</div>
                <div className="mission-footer">
                  <span className="created-date">
                    Created: {formatTimestamp(mission.created_at)}
                  </span>
                  {mission.updated_at !== mission.created_at && (
                    <span className="updated-date">
                      Updated: {formatTimestamp(mission.updated_at)}
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default MissionLog;