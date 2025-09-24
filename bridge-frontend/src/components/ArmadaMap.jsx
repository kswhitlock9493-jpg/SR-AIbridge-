import React, { useState } from 'react';
import { getArmadaStatus } from '../api';
import { usePolling } from '../hooks/usePolling';

const ArmadaMap = () => {
  const [fleet, setFleet] = useState([]);

  /**
   * Optimized fleet data fetching function
   * Manages armada status data with proper error handling
   */
  const fetchFleetData = async () => {
    const data = await getArmadaStatus();
    setFleet(data);
    return data;
  };

  /**
   * Use 30-second polling for fleet status updates
   * Fleet positions and status don't require high-frequency updates,
   * making 30-second intervals optimal for network efficiency
   */
  const { loading, error, refresh } = usePolling(fetchFleetData, {
    interval: 30000, // 30 seconds - balanced refresh rate for fleet monitoring
    immediate: true,
    debounceDelay: 200
  });

  // Utility function for fleet status visualization
  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'online': return '#00ff00';
      case 'offline': return '#ff4444';
      case 'maintenance': return '#ffaa00';
      case 'mission': return '#00aaff';
      default: return '#888';
    }
  };

  if (loading) {
    return (
      <div className="armada-map">
        <h2>🗺️ Armada Map</h2>
        <div className="loading">Loading fleet data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="armada-map">
        <h2>🗺️ Armada Map</h2>
        <div className="error">Error loading fleet: {error}</div>
        <button onClick={refresh} className="retry-button">Retry</button>
      </div>
    );
  }

  return (
    <div className="armada-map">
      <div className="header">
        <h2>🗺️ Armada Map</h2>
        {/* Manual refresh for immediate fleet status updates */}
        <button onClick={refresh} className="refresh-button">🔄 Refresh</button>
      </div>
      
      <div className="fleet-container">
        {fleet.length === 0 ? (
          <div className="no-fleet">No fleet data available</div>
        ) : (
          <div className="fleet-grid">
            {fleet.map((ship) => (
              <div key={ship.id} className="ship-card">
                <div className="ship-header">
                  <h3 className="ship-name">{ship.name}</h3>
                  <span 
                    className="status-indicator" 
                    style={{ color: getStatusColor(ship.status) }}
                  >
                    ● {ship.status?.toUpperCase()}
                  </span>
                </div>
                <div className="ship-details">
                  <div className="detail-row">
                    <span className="label">Type:</span>
                    <span className="value">{ship.type}</span>
                  </div>
                  <div className="detail-row">
                    <span className="label">Location:</span>
                    <span className="value">{ship.location}</span>
                  </div>
                  <div className="detail-row">
                    <span className="label">Captain:</span>
                    <span className="value">{ship.captain}</span>
                  </div>
                  {ship.mission && (
                    <div className="detail-row">
                      <span className="label">Mission:</span>
                      <span className="value">{ship.mission}</span>
                    </div>
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

export default ArmadaMap;