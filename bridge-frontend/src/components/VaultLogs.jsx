import React, { useState, useEffect } from 'react';
import { getVaultLogs, addVaultLog } from '../api';

const VaultLogs = () => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showAddForm, setShowAddForm] = useState(false);
  const [newLog, setNewLog] = useState({
    title: '',
    content: '',
    category: 'doctrine',
    classification: 'unclassified'
  });
  const [filters, setFilters] = useState({
    category: 'all',
    classification: 'all',
    search: ''
  });
  const [lastUpdate, setLastUpdate] = useState(new Date());

  // Fetch vault logs from backend
  const fetchVaultLogs = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getVaultLogs();
      setLogs(Array.isArray(data) ? data : []);
      setLastUpdate(new Date());
    } catch (err) {
      console.error('Failed to fetch vault logs:', err);
      setError('Failed to load vault logs: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  // Add new vault log
  const handleAddLog = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      await addVaultLog({
        ...newLog,
        timestamp: new Date().toISOString()
      });
      setNewLog({ title: '', content: '', category: 'doctrine', classification: 'unclassified' });
      setShowAddForm(false);
      await fetchVaultLogs(); // Refresh logs list
    } catch (err) {
      console.error('Failed to add vault log:', err);
      setError('Failed to add vault log: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  // Filter and search logs
  const getFilteredLogs = () => {
    let filtered = [...logs];

    // Category filter
    if (filters.category !== 'all') {
      filtered = filtered.filter(log => log.category === filters.category);
    }

    // Classification filter
    if (filters.classification !== 'all') {
      filtered = filtered.filter(log => log.classification === filters.classification);
    }

    // Search filter
    if (filters.search.trim()) {
      const searchLower = filters.search.toLowerCase();
      filtered = filtered.filter(log =>
        (log.title || '').toLowerCase().includes(searchLower) ||
        (log.content || '').toLowerCase().includes(searchLower)
      );
    }

    return filtered.sort((a, b) => {
      const dateA = new Date(a.timestamp || a.created_at || Date.now());
      const dateB = new Date(b.timestamp || b.created_at || Date.now());
      return dateB - dateA; // Most recent first
    });
  };

  // Get classification color
  const getClassificationColor = (classification) => {
    switch (classification) {
      case 'top_secret':
        return '#dc3545';
      case 'secret':
        return '#fd7e14';
      case 'confidential':
        return '#ffc107';
      case 'restricted':
        return '#20c997';
      case 'unclassified':
        return '#28a745';
      default:
        return '#6c757d';
    }
  };

  // Get category icon
  const getCategoryIcon = (category) => {
    switch (category) {
      case 'doctrine':
        return '📜';
      case 'intelligence':
        return '🔍';
      case 'operations':
        return '⚔️';
      case 'personnel':
        return '👥';
      case 'technical':
        return '🔧';
      case 'historical':
        return '📚';
      default:
        return '📝';
    }
  };

  // Initial load and periodic refresh
  useEffect(() => {
    fetchVaultLogs();
    const interval = setInterval(fetchVaultLogs, 60000); // Refresh every minute
    return () => clearInterval(interval);
  }, []);

  const filteredLogs = getFilteredLogs();

  return (
    <div className="vault-logs">
      <div className="vault-logs-header">
        <h2>📜 Vault Logs - Doctrine Archive</h2>
        <div className="header-actions">
          <span className="last-update">
            Last Updated: {lastUpdate.toLocaleTimeString()}
          </span>
          <button onClick={fetchVaultLogs} className="refresh-btn">
            🔄 Refresh
          </button>
          <button onClick={() => setShowAddForm(true)} className="add-btn">
            ➕ Add Entry
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

      {/* Filters */}
      <div className="vault-filters">
        <div className="filter-group">
          <label>Category:</label>
          <select
            value={filters.category}
            onChange={(e) => setFilters({ ...filters, category: e.target.value })}
          >
            <option value="all">All Categories</option>
            <option value="doctrine">Doctrine</option>
            <option value="intelligence">Intelligence</option>
            <option value="operations">Operations</option>
            <option value="personnel">Personnel</option>
            <option value="technical">Technical</option>
            <option value="historical">Historical</option>
          </select>
        </div>

        <div className="filter-group">
          <label>Classification:</label>
          <select
            value={filters.classification}
            onChange={(e) => setFilters({ ...filters, classification: e.target.value })}
          >
            <option value="all">All Classifications</option>
            <option value="unclassified">Unclassified</option>
            <option value="restricted">Restricted</option>
            <option value="confidential">Confidential</option>
            <option value="secret">Secret</option>
            <option value="top_secret">Top Secret</option>
          </select>
        </div>

        <div className="filter-group">
          <label>Search:</label>
          <input
            type="text"
            placeholder="Search vault logs..."
            value={filters.search}
            onChange={(e) => setFilters({ ...filters, search: e.target.value })}
          />
        </div>
      </div>

      {/* Vault Statistics */}
      <div className="vault-stats">
        <div className="stat-item">
          <span className="stat-label">Total Entries:</span>
          <span className="stat-value">{logs.length}</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Categories:</span>
          <span className="stat-value">
            {new Set(logs.map(log => log.category || 'doctrine')).size}
          </span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Classified:</span>
          <span className="stat-value">
            {logs.filter(log => log.classification !== 'unclassified').length}
          </span>
        </div>
      </div>

      {/* Logs List */}
      <div className="logs-container">
        {loading && logs.length === 0 ? (
          <div className="loading-spinner">
            <span>⏳</span>
            <p>Loading vault logs...</p>
          </div>
        ) : filteredLogs.length > 0 ? (
          <div className="logs-list">
            {filteredLogs.map((log) => (
              <div key={log.id} className="log-entry">
                <div className="log-header">
                  <div className="log-title">
                    <span className="category-icon">
                      {getCategoryIcon(log.category)}
                    </span>
                    <span className="title-text">
                      {log.title || `Entry ${log.id}`}
                    </span>
                  </div>
                  <div className="log-meta">
                    <span
                      className="classification-badge"
                      style={{ backgroundColor: getClassificationColor(log.classification) }}
                    >
                      {(log.classification || 'unclassified').toUpperCase()}
                    </span>
                  </div>
                </div>

                <div className="log-content">
                  {log.content || 'No content available'}
                </div>

                <div className="log-footer">
                  <div className="log-details">
                    <span className="detail-item">
                      Category: {log.category || 'doctrine'}
                    </span>
                    <span className="detail-item">
                      Added: {log.timestamp || log.created_at 
                        ? new Date(log.timestamp || log.created_at).toLocaleDateString()
                        : 'Unknown'
                      }
                    </span>
                    {log.author && (
                      <span className="detail-item">
                        Author: {log.author}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="no-logs">
            <span>📜</span>
            <p>No vault logs found matching your criteria</p>
            <button onClick={() => setShowAddForm(true)} className="add-btn">
              Add First Entry
            </button>
          </div>
        )}
      </div>

      {/* Add Log Modal */}
      {showAddForm && (
        <div className="modal-overlay">
          <div className="modal">
            <div className="modal-header">
              <h3>Add Vault Entry</h3>
              <button onClick={() => setShowAddForm(false)} className="close-btn">
                ✕
              </button>
            </div>
            <form onSubmit={handleAddLog} className="log-form">
              <div className="form-group">
                <label>Title:</label>
                <input
                  type="text"
                  value={newLog.title}
                  onChange={(e) => setNewLog({ ...newLog, title: e.target.value })}
                  required
                  placeholder="Enter log title"
                />
              </div>
              <div className="form-group">
                <label>Content:</label>
                <textarea
                  value={newLog.content}
                  onChange={(e) => setNewLog({ ...newLog, content: e.target.value })}
                  required
                  placeholder="Enter log content"
                  rows="6"
                />
              </div>
              <div className="form-group">
                <label>Category:</label>
                <select
                  value={newLog.category}
                  onChange={(e) => setNewLog({ ...newLog, category: e.target.value })}
                >
                  <option value="doctrine">Doctrine</option>
                  <option value="intelligence">Intelligence</option>
                  <option value="operations">Operations</option>
                  <option value="personnel">Personnel</option>
                  <option value="technical">Technical</option>
                  <option value="historical">Historical</option>
                </select>
              </div>
              <div className="form-group">
                <label>Classification:</label>
                <select
                  value={newLog.classification}
                  onChange={(e) => setNewLog({ ...newLog, classification: e.target.value })}
                >
                  <option value="unclassified">Unclassified</option>
                  <option value="restricted">Restricted</option>
                  <option value="confidential">Confidential</option>
                  <option value="secret">Secret</option>
                  <option value="top_secret">Top Secret</option>
                </select>
              </div>
              <div className="form-actions">
                <button type="button" onClick={() => setShowAddForm(false)} className="cancel-btn">
                  Cancel
                </button>
                <button type="submit" disabled={loading} className="submit-btn">
                  {loading ? 'Adding...' : 'Add Entry'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default VaultLogs;