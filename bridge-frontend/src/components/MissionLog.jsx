import React, { useState, useEffect } from 'react';
import { getMissions } from '../api';
import { usePolling } from '../hooks/usePolling';

const MissionLog = ({ refreshKey, realTimeMissions = [] }) => {
  const [missions, setMissions] = useState([]);

  /**
   * Enhanced mission data fetching with real-time integration
   */
  const fetchMissions = async () => {
    const data = await getMissions();
    setMissions(data);
    return data;
  };

  /**
   * Merge real-time mission updates with API data
   */
  useEffect(() => {
    if (realTimeMissions.length > 0) {
      setMissions(prevMissions => {
        const missionMap = new Map(prevMissions.map(m => [m.id, m]));
        
        // Update with real-time data
        realTimeMissions.forEach(rtMission => {
          missionMap.set(rtMission.id, { ...missionMap.get(rtMission.id), ...rtMission });
        });
        
        return Array.from(missionMap.values())
          .sort((a, b) => new Date(b.updated_at || b.created_at) - new Date(a.updated_at || a.created_at));
      });
    }
  }, [realTimeMissions]);

  /**
   * Reduced polling frequency due to real-time updates
   */
  const { loading, error, refresh } = usePolling(fetchMissions, {
    interval: 60000, // 60 seconds - reduced due to real-time updates
    immediate: true,
    debounceDelay: 200
  });

  // Support instant refresh when new missions are dispatched via refreshKey prop
  useEffect(() => {
    if (refreshKey) {
      refresh();
    }
  }, [refreshKey, refresh]);

  // Utility functions for mission data formatting
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
        <button onClick={refresh} className="retry-button">Retry</button>
      </div>
    );
  }

  return (
    <div className="mission-log">
      <div className="header">
        <h2>🚀 Mission Log</h2>
        {/* Manual refresh for immediate mission status updates */}
        <button onClick={refresh} className="refresh-button">🔄 Refresh</button>
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