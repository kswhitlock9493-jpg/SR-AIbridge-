import React, { useState, useEffect } from 'react';
import { useBridge } from '../hooks/useBridge';

const ArmadaMap = () => {
  const { 
    armadaStatus, 
    fleetData, 
    realTimeData, 
    loading, 
    error, 
    refreshData 
  } = useBridge();
  
  const [displayFleet, setDisplayFleet] = useState({ fleet: [], summary: {} });

  /**
   * Update display fleet with real-time data
   */
  useEffect(() => {
    const realTimeFleet = realTimeData.fleetData || [];
    
    // Combine armada status and fleet data from bridge context
    const combined = {
      fleet: fleetData && fleetData.length > 0 ? fleetData : realTimeFleet,
      summary: armadaStatus || {},
      last_updated: new Date().toISOString()
    };
    
    setDisplayFleet(combined);
    
    if (realTimeFleet.length > 0) {
      console.log('📡 Real-time fleet updates available:', realTimeFleet.length);
    }
  }, [armadaStatus, fleetData, realTimeData.fleetData]);

  // Utility functions for fleet visualization
  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'online': return '#00ff00';
      case 'offline': return '#ff4444';
      case 'maintenance': return '#ffaa00';
      case 'patrol': return '#00aaff';
      default: return '#888';
    }
  };

  const getStatusIcon = (status) => {
    switch (status?.toLowerCase()) {
      case 'online': return '🟢';
      case 'offline': return '🔴';
      case 'maintenance': return '🟡';
      case 'patrol': return '🔵';
      default: return '⚪';
    }
  };

  const getShipIcon = (name) => {
    if (name.toLowerCase().includes('flagship')) return '🚀';
    if (name.toLowerCase().includes('frigate')) return '🛳️';
    if (name.toLowerCase().includes('scout')) return '🛸';
    return '⚓';
  };

  if (loading && displayFleet.fleet.length === 0) {
    return (
      <div className="armada-map">
        <h2>🗺️ Armada Map</h2>
        <div className="loading">Connecting to fleet command...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="armada-map">
        <h2>🗺️ Armada Map</h2>
        <div className="error">Error connecting to fleet: {error}</div>
        <button onClick={() => refreshData('armada')} className="retry-button">🔄 Reconnect</button>
      </div>
    );
  }

  const { fleet = [], summary = {} } = fleetData;

  return (
    <div className="armada-map">
      <div className="header">
        <h2>🗺️ Armada Map</h2>
        <div className="header-info">
          <span className="live-indicator">🔴 LIVE</span>
          <button onClick={() => refreshData('armada')} className="refresh-button">🔄 Refresh</button>
        </div>
      </div>
      
      {summary.total_ships && (
        <div className="fleet-summary">
          <div className="summary-stats">
            <div className="stat-item">
              <span className="stat-value">{summary.total_ships}</span>
              <span className="stat-label">Total Ships</span>
            </div>
            <div className="stat-item online">
              <span className="stat-value">{summary.online}</span>
              <span className="stat-label">Online</span>
            </div>
            <div className="stat-item patrol">
              <span className="stat-value">{summary.patrol}</span>
              <span className="stat-label">Patrol</span>
            </div>
            <div className="stat-item offline">
              <span className="stat-value">{summary.offline}</span>
              <span className="stat-label">Offline</span>
            </div>
          </div>
        </div>
      )}
      
      <div className="fleet-container">
        {fleet.length === 0 ? (
          <div className="no-fleet">
            <div className="placeholder-icon">🚢</div>
            <div>Waiting for fleet data...</div>
            <div className="subtitle">Live fleet tracking is active</div>
          </div>
        ) : (
          <div className="fleet-grid">
            {fleet.map((ship) => (
              <div 
                key={ship.id} 
                className={`ship-card ${ship.operational ? 'operational' : 'non-operational'}`}
              >
                <div className="ship-header">
                  <div className="ship-title">
                    <span className="ship-icon">{getShipIcon(ship.name)}</span>
                    <h3 className="ship-name">{ship.name}</h3>
                  </div>
                  <div className="status-section">
                    <span className="status-icon">{getStatusIcon(ship.status)}</span>
                    <span 
                      className="status-text" 
                      style={{ color: getStatusColor(ship.status) }}
                    >
                      {ship.status?.toUpperCase()}
                    </span>
                  </div>
                </div>
                <div className="ship-details">
                  <div className="detail-row">
                    <span className="label">📍 Location:</span>
                    <span className="value">{ship.location}</span>
                  </div>
                  {ship.patrol_sectors && ship.patrol_sectors.length > 0 && (
                    <div className="detail-row">
                      <span className="label">🎯 Patrol:</span>
                      <span className="value">{ship.patrol_sectors.join(', ')}</span>
                    </div>
                  )}
                  <div className="detail-row">
                    <span className="label">📡 Last Report:</span>
                    <span className="value">{new Date(ship.last_reported).toLocaleTimeString()}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
      
      <div className="fleet-footer">
        <div className="status-info">
          Last updated: {summary.last_updated ? new Date(summary.last_updated).toLocaleString() : 'Live'} | 
          Real-time tracking: Active
        </div>
      </div>
    </div>
  );
};

export default ArmadaMap;