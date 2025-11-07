import { useState, useEffect, useCallback } from 'react';
import { getMissions, createMission, updateMissionProgress, updateMissionStatus } from '../api';

const MissionLog = () => {
  const [missions, setMissions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [currentCaptain, setCurrentCaptain] = useState('Captain Alpha'); // Current captain context
  const [newMission, setNewMission] = useState({
    title: '',
    description: '',
    priority: 'medium',
    type: 'standard',
    progress: 0 // Add progress tracking
  });
  const [filters, setFilters] = useState({
    status: 'all',
    priority: 'all',
    search: ''
  });
  const [lastUpdate, setLastUpdate] = useState(new Date());

  // Fetch missions from backend (captain-filtered)
  const fetchMissions = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      // Fetch only captain-owned missions
      const data = await getMissions(currentCaptain, 'captain');
      setMissions(Array.isArray(data) ? data : []);
      setLastUpdate(new Date());
    } catch (err) {
      console.error('Failed to fetch missions:', err);
      setError('Failed to load missions: ' + err.message);
    } finally {
      setLoading(false);
    }
  }, [currentCaptain]);

  // Create new mission
  const handleCreateMission = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      // Include captain ownership in mission creation
      await createMission({
        ...newMission,
        captain: currentCaptain,
        role: 'captain',
        progress: 0 // Initialize progress
      });
      setNewMission({ title: '', description: '', priority: 'medium', type: 'standard', progress: 0 });
      setShowCreateForm(false);
      await fetchMissions(); // Refresh missions list
    } catch (err) {
      console.error('Failed to create mission:', err);
      setError('Failed to create mission: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  // Update mission progress
  const handleProgressUpdate = async (missionId, newProgress) => {
    try {
      // Update mission progress using dedicated function
      await updateMissionProgress(missionId, newProgress);
      await fetchMissions(); // Refresh missions list
    } catch (err) {
      console.error('Failed to update mission progress:', err);
      // Update locally as fallback
      setMissions(missions.map(m => 
        m.id === missionId ? { ...m, progress: newProgress } : m
      ));
    }
  };

  // Update mission status
  const handleStatusUpdate = async (missionId, newStatus) => {
    try {
      await updateMissionStatus(missionId, newStatus);
      await fetchMissions(); // Refresh missions list
    } catch (err) {
      console.error('Failed to update mission status:', err);
      setError('Failed to update mission status: ' + err.message);
    }
  };

  // Filter and search missions
  const getFilteredMissions = () => {
    let filtered = [...missions];

    // Status filter
    if (filters.status !== 'all') {
      filtered = filtered.filter(mission => mission.status === filters.status);
    }

    // Priority filter
    if (filters.priority !== 'all') {
      filtered = filtered.filter(mission => mission.priority === filters.priority);
    }

    // Search filter
    if (filters.search.trim()) {
      const searchLower = filters.search.toLowerCase();
      filtered = filtered.filter(mission =>
        (mission.title || '').toLowerCase().includes(searchLower) ||
        (mission.description || '').toLowerCase().includes(searchLower)
      );
    }

    return filtered.sort((a, b) => {
      const dateA = new Date(a.created_at || Date.now());
      const dateB = new Date(b.created_at || Date.now());
      return dateB - dateA; // Most recent first
    });
  };

  // Get status color
  const getStatusColor = (status) => {
    switch (status) {
      case 'active':
      case 'in_progress':
        return '#28a745';
      case 'completed':
        return '#007bff';
      case 'failed':
        return '#dc3545';
      case 'pending':
        return '#ffc107';
      default:
        return '#6c757d';
    }
  };

  // Get priority color
  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high':
        return '#dc3545';
      case 'medium':
        return '#ffc107';
      case 'low':
        return '#28a745';
      default:
        return '#6c757d';
    }
  };

  // Initial load and periodic refresh
  useEffect(() => {
    fetchMissions();
    const interval = setInterval(fetchMissions, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, [fetchMissions]); // Re-fetch when captain changes

  const filteredMissions = getFilteredMissions();

  return (
    <div className="mission-log">
      <div className="mission-log-header">
        <h2>🚀 Mission Log</h2>
        <div className="header-actions">
          <span className="last-update">
            Last Updated: {lastUpdate.toLocaleTimeString()}
          </span>
          <button onClick={fetchMissions} className="refresh-btn">
            🔄 Refresh
          </button>
          <button onClick={() => setShowCreateForm(true)} className="create-btn">
            ➕ New Mission
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

      {/* Captain Selector */}
      <div className="captain-selector">
        <label>Captain:</label>
        <select 
          value={currentCaptain}
          onChange={(e) => setCurrentCaptain(e.target.value)}
        >
          <option value="Captain Alpha">Captain Alpha</option>
          <option value="Captain Beta">Captain Beta</option>
          <option value="Captain Gamma">Captain Gamma</option>
          <option value="Captain Delta">Captain Delta</option>
          <option value="Captain Epsilon">Captain Epsilon</option>
        </select>
        <span className="info-text">📋 Viewing missions for {currentCaptain}</span>
      </div>

      {/* Filters */}
      <div className="mission-filters">
        <div className="filter-group">
          <label>Status:</label>
          <select
            value={filters.status}
            onChange={(e) => setFilters({ ...filters, status: e.target.value })}
          >
            <option value="all">All Statuses</option>
            <option value="pending">Pending</option>
            <option value="active">Active</option>
            <option value="in_progress">In Progress</option>
            <option value="completed">Completed</option>
            <option value="failed">Failed</option>
          </select>
        </div>

        <div className="filter-group">
          <label>Priority:</label>
          <select
            value={filters.priority}
            onChange={(e) => setFilters({ ...filters, priority: e.target.value })}
          >
            <option value="all">All Priorities</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
        </div>

        <div className="filter-group">
          <label>Search:</label>
          <input
            type="text"
            placeholder="Search missions..."
            value={filters.search}
            onChange={(e) => setFilters({ ...filters, search: e.target.value })}
          />
        </div>
      </div>

      {/* Mission Statistics */}
      <div className="mission-stats">
        <div className="stat-item">
          <span className="stat-label">Total Missions:</span>
          <span className="stat-value">{missions.length}</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Active:</span>
          <span className="stat-value">
            {missions.filter(m => m.status === 'active' || m.status === 'in_progress').length}
          </span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Completed:</span>
          <span className="stat-value">
            {missions.filter(m => m.status === 'completed').length}
          </span>
        </div>
      </div>

      {/* Missions List */}
      <div className="missions-container">
        {loading && missions.length === 0 ? (
          <div className="loading-spinner">
            <span>⏳</span>
            <p>Loading missions...</p>
          </div>
        ) : filteredMissions.length > 0 ? (
          <div className="missions-grid">
            {filteredMissions.map((mission) => (
              <div key={mission.id} className="mission-card">
                <div className="mission-header">
                  <div className="mission-title">
                    {mission.title || `Mission ${mission.id}`}
                  </div>
                  <div className="mission-meta">
                    <span
                      className="status-badge"
                      style={{ backgroundColor: getStatusColor(mission.status) }}
                    >
                      {mission.status || 'pending'}
                    </span>
                    <span
                      className="priority-badge"
                      style={{ backgroundColor: getPriorityColor(mission.priority) }}
                    >
                      {mission.priority || 'medium'}
                    </span>
                  </div>
                </div>

                <div className="mission-description">
                  {mission.description || 'No description provided'}
                </div>

                <div className="mission-details">
                  <div className="detail-item">
                    <span>Created:</span>
                    <span>
                      {mission.created_at 
                        ? new Date(mission.created_at).toLocaleDateString()
                        : 'Unknown'
                      }
                    </span>
                  </div>
                  <div className="detail-item">
                    <span>Type:</span>
                    <span>{mission.type || 'standard'}</span>
                  </div>
                  {mission.agent_id && (
                    <div className="detail-item">
                      <span>Assigned Agent:</span>
                      <span>{mission.agent_id}</span>
                    </div>
                  )}
                </div>

                {/* Real-time Progress Tracking */}
                {(mission.status === 'active' || mission.status === 'in_progress') && (
                  <div className="mission-progress" style={{
                    marginTop: '12px',
                    marginBottom: '12px'
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                      <span style={{ fontSize: '14px', fontWeight: 'bold' }}>Progress</span>
                      <span style={{ fontSize: '14px' }}>{mission.progress || 0}%</span>
                    </div>
                    <div style={{
                      width: '100%',
                      height: '20px',
                      backgroundColor: 'rgba(255, 255, 255, 0.1)',
                      borderRadius: '10px',
                      overflow: 'hidden',
                      border: '1px solid rgba(255, 255, 255, 0.2)'
                    }}>
                      <div style={{
                        width: `${mission.progress || 0}%`,
                        height: '100%',
                        backgroundColor: '#28a745',
                        transition: 'width 0.3s ease',
                        borderRadius: '10px'
                      }} />
                    </div>
                    {/* Progress controls */}
                    <div style={{
                      display: 'flex',
                      gap: '4px',
                      marginTop: '8px',
                      justifyContent: 'center'
                    }}>
                      <button
                        onClick={() => handleProgressUpdate(mission.id, Math.max(0, (mission.progress || 0) - 10))}
                        style={{
                          padding: '4px 8px',
                          fontSize: '12px',
                          backgroundColor: '#6c757d',
                          color: 'white',
                          border: 'none',
                          borderRadius: '4px',
                          cursor: 'pointer'
                        }}
                      >
                        -10%
                      </button>
                      <button
                        onClick={() => handleProgressUpdate(mission.id, Math.min(100, (mission.progress || 0) + 10))}
                        style={{
                          padding: '4px 8px',
                          fontSize: '12px',
                          backgroundColor: '#28a745',
                          color: 'white',
                          border: 'none',
                          borderRadius: '4px',
                          cursor: 'pointer'
                        }}
                      >
                        +10%
                      </button>
                      <button
                        onClick={() => handleProgressUpdate(mission.id, Math.min(100, (mission.progress || 0) + 25))}
                        style={{
                          padding: '4px 8px',
                          fontSize: '12px',
                          backgroundColor: '#007bff',
                          color: 'white',
                          border: 'none',
                          borderRadius: '4px',
                          cursor: 'pointer'
                        }}
                      >
                        +25%
                      </button>
                    </div>
                  </div>
                )}

                <div className="mission-actions">
                  {mission.status === 'pending' && (
                    <button
                      onClick={() => handleStatusUpdate(mission.id, 'active')}
                      className="action-btn activate"
                    >
                      🚀 Activate
                    </button>
                  )}
                  {(mission.status === 'active' || mission.status === 'in_progress') && (
                    <button
                      onClick={() => handleStatusUpdate(mission.id, 'completed')}
                      className="action-btn complete"
                    >
                      ✅ Complete
                    </button>
                  )}
                  {mission.status !== 'failed' && mission.status !== 'completed' && (
                    <button
                      onClick={() => handleStatusUpdate(mission.id, 'failed')}
                      className="action-btn fail"
                    >
                      ❌ Fail
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="no-missions">
            <span>📋</span>
            <p>No missions found matching your criteria</p>
            <button onClick={() => setShowCreateForm(true)} className="create-btn">
              Create First Mission
            </button>
          </div>
        )}
      </div>

      {/* Create Mission Modal */}
      {showCreateForm && (
        <div className="modal-overlay">
          <div className="modal">
            <div className="modal-header">
              <h3>Create New Mission</h3>
              <button onClick={() => setShowCreateForm(false)} className="close-btn">
                ✕
              </button>
            </div>
            <form onSubmit={handleCreateMission} className="mission-form">
              <div className="form-group">
                <label>Title:</label>
                <input
                  type="text"
                  value={newMission.title}
                  onChange={(e) => setNewMission({ ...newMission, title: e.target.value })}
                  required
                  placeholder="Enter mission title"
                />
              </div>
              <div className="form-group">
                <label>Description:</label>
                <textarea
                  value={newMission.description}
                  onChange={(e) => setNewMission({ ...newMission, description: e.target.value })}
                  placeholder="Enter mission description"
                  rows="3"
                />
              </div>
              <div className="form-group">
                <label>Priority:</label>
                <select
                  value={newMission.priority}
                  onChange={(e) => setNewMission({ ...newMission, priority: e.target.value })}
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                </select>
              </div>
              <div className="form-group">
                <label>Type:</label>
                <select
                  value={newMission.type}
                  onChange={(e) => setNewMission({ ...newMission, type: e.target.value })}
                >
                  <option value="standard">Standard</option>
                  <option value="reconnaissance">Reconnaissance</option>
                  <option value="combat">Combat</option>
                  <option value="diplomatic">Diplomatic</option>
                  <option value="exploration">Exploration</option>
                </select>
              </div>
              <div className="form-actions">
                <button type="button" onClick={() => setShowCreateForm(false)} className="cancel-btn">
                  Cancel
                </button>
                <button type="submit" disabled={loading} className="submit-btn">
                  {loading ? 'Creating...' : 'Create Mission'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default MissionLog;