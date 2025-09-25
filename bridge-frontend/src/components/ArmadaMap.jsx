import { useState, useEffect } from 'react';
import { getArmadaStatus, getFleetData } from '../api';

const ArmadaMap = () => {
  const [armadaStatus, setArmadaStatus] = useState({});
  const [fleetData, setFleetData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedShip, setSelectedShip] = useState(null);
  const [viewMode, setViewMode] = useState('grid'); // 'grid' or 'map'
  const [filters, setFilters] = useState({
    status: 'all',
    type: 'all',
    search: ''
  });
  const [lastUpdate, setLastUpdate] = useState(new Date());

  // Fetch armada data from backend
  const fetchArmadaData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [statusData, fleetInfo] = await Promise.allSettled([
        getArmadaStatus(),
        getFleetData()
      ]);

      if (statusData.status === 'fulfilled') {
        setArmadaStatus(statusData.value || {});
      }

      if (fleetInfo.status === 'fulfilled') {
        const fleet = fleetInfo.value;
        // Handle different response formats
        if (Array.isArray(fleet)) {
          setFleetData(fleet);
        } else if (fleet && Array.isArray(fleet.ships)) {
          setFleetData(fleet.ships);
        } else if (fleet && Array.isArray(fleet.fleet)) {
          setFleetData(fleet.fleet);
        } else {
          setFleetData([]);
        }
      }

      setLastUpdate(new Date());
    } catch (err) {
      console.error('Failed to fetch armada data:', err);
      setError('Failed to load armada data: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  // Filter fleet data
  const getFilteredFleet = () => {
    let filtered = [...fleetData];

    // Status filter
    if (filters.status !== 'all') {
      filtered = filtered.filter(ship => ship.status === filters.status);
    }

    // Type filter
    if (filters.type !== 'all') {
      filtered = filtered.filter(ship => ship.type === filters.type);
    }

    // Search filter
    if (filters.search.trim()) {
      const searchLower = filters.search.toLowerCase();
      filtered = filtered.filter(ship =>
        (ship.name || '').toLowerCase().includes(searchLower) ||
        (ship.callsign || '').toLowerCase().includes(searchLower) ||
        (ship.location || '').toLowerCase().includes(searchLower)
      );
    }

    return filtered;
  };

  // Get status color
  const getStatusColor = (status) => {
    switch (status) {
      case 'active':
      case 'operational':
      case 'online':
        return '#28a745';
      case 'standby':
      case 'idle':
        return '#ffc107';
      case 'offline':
      case 'maintenance':
        return '#6c757d';
      case 'combat':
      case 'engaged':
        return '#dc3545';
      case 'patrol':
      case 'mission':
        return '#007bff';
      default:
        return '#6c757d';
    }
  };

  // Get ship type icon
  const getShipTypeIcon = (type) => {
    switch (type) {
      case 'battleship':
      case 'dreadnought':
        return '🚢';
      case 'cruiser':
        return '🛳️';
      case 'destroyer':
        return '⚓';
      case 'frigate':
        return '🛥️';
      case 'scout':
      case 'reconnaissance':
        return '🔍';
      case 'carrier':
        return '✈️';
      case 'transport':
        return '📦';
      default:
        return '🚁';
    }
  };

  // Generate mock coordinates for visual representation
  const getShipCoordinates = (ship, index) => {
    const seed = ship.id || index;
    const x = 50 + (seed * 37) % 40 - 20; // Random x between 30-70%
    const y = 50 + (seed * 41) % 40 - 20; // Random y between 30-70%
    return { x, y };
  };

  // Initial load and periodic refresh
  useEffect(() => {
    fetchArmadaData();
    const interval = setInterval(fetchArmadaData, 45000); // Refresh every 45 seconds
    return () => clearInterval(interval);
  }, []);

  const filteredFleet = getFilteredFleet();

  return (
    <div className="armada-map">
      <div className="armada-header">
        <h2>🗺️ Armada Tactical Map</h2>
        <div className="header-actions">
          <span className="last-update">
            Last Updated: {lastUpdate.toLocaleTimeString()}
          </span>
          <div className="view-mode-toggle">
            <button
              className={viewMode === 'grid' ? 'active' : ''}
              onClick={() => setViewMode('grid')}
            >
              📋 Grid
            </button>
            <button
              className={viewMode === 'map' ? 'active' : ''}
              onClick={() => setViewMode('map')}
            >
              🗺️ Map
            </button>
          </div>
          <button onClick={fetchArmadaData} className="refresh-btn">
            🔄 Refresh
          </button>
        </div>
      </div>

      {error && (
        <div className="error-banner">
          <span>⚠️</span>
          <span>{error}</span>
          <button onClick={() => setError(null)}>✕</button>
        </div>
      )}

      {/* Armada Status Overview */}
      <div className="armada-overview">
        <div className="overview-stats">
          <div className="stat-item">
            <span className="stat-label">Fleet Size:</span>
            <span className="stat-value">{fleetData.length}</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Operational:</span>
            <span className="stat-value">
              {fleetData.filter(ship => ship.status === 'active' || ship.status === 'operational').length}
            </span>
          </div>
          <div className="stat-item">
            <span className="stat-label">On Mission:</span>
            <span className="stat-value">
              {fleetData.filter(ship => ship.status === 'mission' || ship.status === 'patrol').length}
            </span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Fleet Status:</span>
            <span className="stat-value">{armadaStatus.status || 'Standby'}</span>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="armada-filters">
        <div className="filter-group">
          <label>Status:</label>
          <select
            value={filters.status}
            onChange={(e) => setFilters({ ...filters, status: e.target.value })}
          >
            <option value="all">All Statuses</option>
            <option value="active">Active</option>
            <option value="operational">Operational</option>
            <option value="standby">Standby</option>
            <option value="patrol">Patrol</option>
            <option value="mission">Mission</option>
            <option value="offline">Offline</option>
            <option value="maintenance">Maintenance</option>
          </select>
        </div>

        <div className="filter-group">
          <label>Type:</label>
          <select
            value={filters.type}
            onChange={(e) => setFilters({ ...filters, type: e.target.value })}
          >
            <option value="all">All Types</option>
            <option value="battleship">Battleship</option>
            <option value="cruiser">Cruiser</option>
            <option value="destroyer">Destroyer</option>
            <option value="frigate">Frigate</option>
            <option value="scout">Scout</option>
            <option value="carrier">Carrier</option>
            <option value="transport">Transport</option>
          </select>
        </div>

        <div className="filter-group">
          <label>Search:</label>
          <input
            type="text"
            placeholder="Search ships..."
            value={filters.search}
            onChange={(e) => setFilters({ ...filters, search: e.target.value })}
          />
        </div>
      </div>

      {/* Main Content */}
      <div className="armada-content">
        {loading && fleetData.length === 0 ? (
          <div className="loading-spinner">
            <span>⏳</span>
            <p>Loading armada data...</p>
          </div>
        ) : filteredFleet.length > 0 ? (
          <>
            {viewMode === 'grid' ? (
              /* Grid View */
              <div className="fleet-grid">
                {filteredFleet.map((ship, index) => (
                  <div
                    key={ship.id || index}
                    className={`ship-card ${selectedShip?.id === ship.id ? 'selected' : ''}`}
                    onClick={() => setSelectedShip(ship)}
                  >
                    <div className="ship-header">
                      <div className="ship-name">
                        <span className="ship-icon">{getShipTypeIcon(ship.type)}</span>
                        <span className="name-text">{ship.name || `Ship ${ship.id || index + 1}`}</span>
                      </div>
                      <div
                        className="status-indicator"
                        style={{ backgroundColor: getStatusColor(ship.status) }}
                      >
                        {ship.status || 'unknown'}
                      </div>
                    </div>

                    <div className="ship-details">
                      <div className="detail-row">
                        <span>Type:</span>
                        <span>{ship.type || 'Unknown'}</span>
                      </div>
                      <div className="detail-row">
                        <span>Callsign:</span>
                        <span>{ship.callsign || 'N/A'}</span>
                      </div>
                      <div className="detail-row">
                        <span>Location:</span>
                        <span>{ship.location || 'Unknown'}</span>
                      </div>
                      {ship.mission && (
                        <div className="detail-row">
                          <span>Mission:</span>
                          <span>{ship.mission}</span>
                        </div>
                      )}
                    </div>

                    <div className="ship-stats">
                      {ship.crew && (
                        <div className="stat">
                          <span>👥 {ship.crew}</span>
                        </div>
                      )}
                      {ship.armament && (
                        <div className="stat">
                          <span>⚔️ {ship.armament}</span>
                        </div>
                      )}
                      {ship.speed && (
                        <div className="stat">
                          <span>🚀 {ship.speed}</span>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              /* Map View */
              <div className="tactical-map">
                <div className="map-container">
                  <div className="map-grid">
                    {/* Grid lines for tactical display */}
                    {Array.from({ length: 10 }, (_, i) => (
                      <div key={`h-${i}`} className="grid-line horizontal" style={{ top: `${i * 10}%` }} />
                    ))}
                    {Array.from({ length: 10 }, (_, i) => (
                      <div key={`v-${i}`} className="grid-line vertical" style={{ left: `${i * 10}%` }} />
                    ))}
                  </div>

                  {/* Ship positions */}
                  {filteredFleet.map((ship, index) => {
                    const { x, y } = getShipCoordinates(ship, index);
                    return (
                      <div
                        key={ship.id || index}
                        className={`ship-marker ${ship.status || 'unknown'} ${
                          selectedShip?.id === ship.id ? 'selected' : ''
                        }`}
                        style={{ left: `${x}%`, top: `${y}%` }}
                        onClick={() => setSelectedShip(ship)}
                        title={`${ship.name || `Ship ${index + 1}`} - ${ship.status || 'unknown'}`}
                      >
                        <span className="ship-icon">{getShipTypeIcon(ship.type)}</span>
                        <span className="ship-label">{ship.name || ship.callsign || `S${index + 1}`}</span>
                      </div>
                    );
                  })}
                </div>

                {/* Map Legend */}
                <div className="map-legend">
                  <h4>🏷️ Legend</h4>
                  <div className="legend-items">
                    <div className="legend-item">
                      <span className="legend-color" style={{ backgroundColor: '#28a745' }}></span>
                      <span>Operational</span>
                    </div>
                    <div className="legend-item">
                      <span className="legend-color" style={{ backgroundColor: '#007bff' }}></span>
                      <span>On Mission</span>
                    </div>
                    <div className="legend-item">
                      <span className="legend-color" style={{ backgroundColor: '#ffc107' }}></span>
                      <span>Standby</span>
                    </div>
                    <div className="legend-item">
                      <span className="legend-color" style={{ backgroundColor: '#6c757d' }}></span>
                      <span>Offline</span>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </>
        ) : (
          <div className="no-fleet">
            <span>🚁</span>
            <p>No ships found matching your criteria</p>
          </div>
        )}
      </div>

      {/* Ship Details Panel */}
      {selectedShip && (
        <div className="ship-details-panel">
          <div className="panel-header">
            <h3>
              {getShipTypeIcon(selectedShip.type)} {selectedShip.name || `Ship ${selectedShip.id}`}
            </h3>
            <button onClick={() => setSelectedShip(null)} className="close-btn">
              ✕
            </button>
          </div>
          <div className="panel-content">
            <div className="detail-section">
              <h4>Status Information</h4>
              <div className="info-grid">
                <div className="info-item">
                  <span>Status:</span>
                  <span
                    className="status-badge"
                    style={{ backgroundColor: getStatusColor(selectedShip.status) }}
                  >
                    {selectedShip.status || 'unknown'}
                  </span>
                </div>
                <div className="info-item">
                  <span>Type:</span>
                  <span>{selectedShip.type || 'Unknown'}</span>
                </div>
                <div className="info-item">
                  <span>Callsign:</span>
                  <span>{selectedShip.callsign || 'N/A'}</span>
                </div>
                <div className="info-item">
                  <span>Location:</span>
                  <span>{selectedShip.location || 'Unknown'}</span>
                </div>
              </div>
            </div>
            
            {selectedShip.mission && (
              <div className="detail-section">
                <h4>Current Mission</h4>
                <p>{selectedShip.mission}</p>
              </div>
            )}

            {(selectedShip.crew || selectedShip.armament || selectedShip.speed) && (
              <div className="detail-section">
                <h4>Specifications</h4>
                <div className="spec-grid">
                  {selectedShip.crew && (
                    <div className="spec-item">
                      <span>👥 Crew:</span>
                      <span>{selectedShip.crew}</span>
                    </div>
                  )}
                  {selectedShip.armament && (
                    <div className="spec-item">
                      <span>⚔️ Armament:</span>
                      <span>{selectedShip.armament}</span>
                    </div>
                  )}
                  {selectedShip.speed && (
                    <div className="spec-item">
                      <span>🚀 Speed:</span>
                      <span>{selectedShip.speed}</span>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default ArmadaMap;