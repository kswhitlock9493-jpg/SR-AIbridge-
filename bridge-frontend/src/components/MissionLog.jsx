import React, { useState, useEffect } from 'react';
import { getMissions, createMission, updateMissionStatus } from '../api';
import { usePolling } from '../hooks/usePolling';

const MissionLog = ({ refreshKey, realTimeMissions = [] }) => {
  const [missions, setMissions] = useState([]);
  const [filteredMissions, setFilteredMissions] = useState([]);
  const [filters, setFilters] = useState({
    status: 'all',
    priority: 'all',
    search: ''
  });
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newMission, setNewMission] = useState({
    title: '',
    description: '',
    priority: 'medium'
  });
  const [sortBy, setSortBy] = useState('created_at');
  const [sortOrder, setSortOrder] = useState('desc');

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
   * Apply filters and sorting to missions
   */
  useEffect(() => {
    let filtered = [...missions];

    // Apply status filter
    if (filters.status !== 'all') {
      filtered = filtered.filter(m => m.status?.toLowerCase() === filters.status);
    }

    // Apply priority filter
    if (filters.priority !== 'all') {
      filtered = filtered.filter(m => m.priority?.toLowerCase() === filters.priority);
    }

    // Apply search filter
    if (filters.search) {
      const searchTerm = filters.search.toLowerCase();
      filtered = filtered.filter(m => 
        m.title?.toLowerCase().includes(searchTerm) || 
        m.description?.toLowerCase().includes(searchTerm)
      );
    }

    // Apply sorting
    filtered.sort((a, b) => {
      const aValue = a[sortBy] || '';
      const bValue = b[sortBy] || '';
      
      if (sortBy.includes('_at')) {
        const aDate = new Date(aValue);
        const bDate = new Date(bValue);
        return sortOrder === 'desc' ? bDate - aDate : aDate - bDate;
      }
      
      const comparison = aValue.toString().localeCompare(bValue.toString());
      return sortOrder === 'desc' ? -comparison : comparison;
    });

    setFilteredMissions(filtered);
  }, [missions, filters, sortBy, sortOrder]);

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

  /**
   * Handle creating new mission
   */
  const handleCreateMission = async (e) => {
    e.preventDefault();
    if (!newMission.title.trim()) return;

    try {
      await createMission({
        ...newMission,
        status: 'planning',
        created_at: new Date().toISOString()
      });
      
      setNewMission({ title: '', description: '', priority: 'medium' });
      setShowCreateForm(false);
      await refresh(); // Refresh missions list
    } catch (err) {
      console.error('Failed to create mission:', err);
    }
  };

  /**
   * Handle updating mission status
   */
  const handleStatusUpdate = async (missionId, newStatus) => {
    try {
      await updateMissionStatus(missionId, newStatus);
      await refresh(); // Refresh missions list
    } catch (err) {
      console.error('Failed to update mission status:', err);
    }
  };

  /**
   * Clear all filters
   */
  const clearFilters = () => {
    setFilters({ status: 'all', priority: 'all', search: '' });
  };

  // Stats for display
  const stats = {
    total: missions.length,
    active: missions.filter(m => m.status === 'active').length,
    completed: missions.filter(m => m.status === 'completed').length,
    failed: missions.filter(m => m.status === 'failed').length
  };

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

  if (loading && missions.length === 0) {
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
        <div className="header-controls">
          <span className="live-indicator">🔴 LIVE</span>
          <button onClick={() => setShowCreateForm(!showCreateForm)} className="create-button">
            ➕ New Mission
          </button>
          <button onClick={refresh} className="refresh-button">🔄 Refresh</button>
        </div>
      </div>

      {/* Mission Statistics */}
      <div className="mission-stats">
        <div className="stat-item">
          <span className="stat-value">{stats.total}</span>
          <span className="stat-label">Total</span>
        </div>
        <div className="stat-item active">
          <span className="stat-value">{stats.active}</span>
          <span className="stat-label">Active</span>
        </div>
        <div className="stat-item completed">
          <span className="stat-value">{stats.completed}</span>
          <span className="stat-label">Completed</span>
        </div>
        <div className="stat-item failed">
          <span className="stat-value">{stats.failed}</span>
          <span className="stat-label">Failed</span>
        </div>
      </div>

      {/* Create Mission Form */}
      {showCreateForm && (
        <div className="create-mission-form">
          <h3>Create New Mission</h3>
          <form onSubmit={handleCreateMission}>
            <div className="form-row">
              <input
                type="text"
                placeholder="Mission title..."
                value={newMission.title}
                onChange={(e) => setNewMission({ ...newMission, title: e.target.value })}
                required
              />
              <select
                value={newMission.priority}
                onChange={(e) => setNewMission({ ...newMission, priority: e.target.value })}
              >
                <option value="low">Low Priority</option>
                <option value="medium">Medium Priority</option>
                <option value="high">High Priority</option>
              </select>
            </div>
            <textarea
              placeholder="Mission description..."
              value={newMission.description}
              onChange={(e) => setNewMission({ ...newMission, description: e.target.value })}
              rows={3}
            />
            <div className="form-actions">
              <button type="submit">Create Mission</button>
              <button type="button" onClick={() => setShowCreateForm(false)}>Cancel</button>
            </div>
          </form>
        </div>
      )}

      {/* Filters */}
      <div className="mission-filters">
        <div className="filter-group">
          <label>Status:</label>
          <select value={filters.status} onChange={(e) => setFilters({ ...filters, status: e.target.value })}>
            <option value="all">All Statuses</option>
            <option value="planning">Planning</option>
            <option value="active">Active</option>
            <option value="completed">Completed</option>
            <option value="failed">Failed</option>
          </select>
        </div>
        
        <div className="filter-group">
          <label>Priority:</label>
          <select value={filters.priority} onChange={(e) => setFilters({ ...filters, priority: e.target.value })}>
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

        <div className="filter-group">
          <label>Sort:</label>
          <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
            <option value="created_at">Created Date</option>
            <option value="updated_at">Updated Date</option>
            <option value="title">Title</option>
            <option value="priority">Priority</option>
            <option value="status">Status</option>
          </select>
          <select value={sortOrder} onChange={(e) => setSortOrder(e.target.value)}>
            <option value="desc">Descending</option>
            <option value="asc">Ascending</option>
          </select>
        </div>

        {(filters.status !== 'all' || filters.priority !== 'all' || filters.search) && (
          <button onClick={clearFilters} className="clear-filters-button">Clear Filters</button>
        )}
      </div>
      
      <div className="missions-container">
        {filteredMissions.length === 0 ? (
          <div className="no-missions">
            {missions.length === 0 ? 'No missions available' : 'No missions match your filters'}
          </div>
        ) : (
          <div className="missions-list">
            {filteredMissions.map((mission, index) => (
              <div key={mission.id} className={`mission-entry ${index < 3 ? 'recent' : ''}`}>
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
                
                {/* Status Update Controls */}
                <div className="mission-controls">
                  <label>Update Status:</label>
                  <select 
                    value={mission.status || 'planning'}
                    onChange={(e) => handleStatusUpdate(mission.id, e.target.value)}
                  >
                    <option value="planning">Planning</option>
                    <option value="active">Active</option>
                    <option value="completed">Completed</option>
                    <option value="failed">Failed</option>
                  </select>
                </div>

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