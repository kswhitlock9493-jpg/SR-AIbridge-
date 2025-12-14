import { useState, useEffect, useCallback } from 'react';
import config from '../config';
import { SovereignRevealGate } from './DeploymentGate.jsx';
import { SilentFailureCapture } from '../services/silent-failure-capture.js';

const BrainConsoleCore = () => {
  const [brainState, setBrainState] = useState({
    memories: [],
    stats: null,
    categories: [],
    loading: true,
    error: null,
    searchQuery: '',
    selectedCategory: '',
    selectedClassification: ''
  });

  const [showAddMemory, setShowAddMemory] = useState(false);
  const [newMemory, setNewMemory] = useState({
    content: '',
    category: 'general',
    classification: 'public',
    metadata: ''
  });

  const API_BASE = config.API_BASE_URL;

  const fetchBrainData = useCallback(async () => {
    try {
      setBrainState(prev => ({ ...prev, loading: true, error: null }));
      
      // Fetch stats, memories, and categories in parallel
      const [statsRes, memoriesRes, categoriesRes] = await Promise.all([
        fetch(`${API_BASE}/brain/stats`),
        fetch(`${API_BASE}/brain/memories?limit=50`),
        fetch(`${API_BASE}/brain/categories`)
      ]);

      if (!statsRes.ok || !memoriesRes.ok || !categoriesRes.ok) {
        throw new Error('Failed to fetch brain data');
      }

      const stats = await statsRes.json();
      const memories = await memoriesRes.json();
      const categoriesData = await categoriesRes.json();

      setBrainState(prev => ({
        ...prev,
        stats,
        memories,
        categories: categoriesData.categories || [],
        loading: false
      }));
      
      // Record successful health check
      SilentFailureCapture.recordHealthCheck('brain-console', true);
    } catch (error) {
      console.error('Brain data fetch error:', error);
      setBrainState(prev => ({
        ...prev,
        error: error.message,
        loading: false
      }));
      
      // Record failure
      SilentFailureCapture.recordHealthCheck('brain-console', false, error);
    }
  }, [API_BASE]);

  useEffect(() => {
    fetchBrainData();
  }, [fetchBrainData]);

  const searchMemories = async () => {
    try {
      setBrainState(prev => ({ ...prev, loading: true }));
      
      const params = new URLSearchParams();
      if (brainState.searchQuery) params.append('query', brainState.searchQuery);
      if (brainState.selectedCategory) params.append('category', brainState.selectedCategory);
      if (brainState.selectedClassification) params.append('classification', brainState.selectedClassification);
      params.append('limit', '50');

      const response = await fetch(`${API_BASE}/brain/memories?${params}`);
      if (!response.ok) throw new Error('Search failed');

      const memories = await response.json();
      setBrainState(prev => ({ ...prev, memories, loading: false }));
    } catch (error) {
      setBrainState(prev => ({ ...prev, error: error.message, loading: false }));
    }
  };

  const addMemory = async () => {
    try {
      const metadata = newMemory.metadata ? JSON.parse(newMemory.metadata) : {};
      
      const response = await fetch(`${API_BASE}/brain/memories`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          content: newMemory.content,
          category: newMemory.category,
          classification: newMemory.classification,
          metadata,
          sign: true
        })
      });

      if (!response.ok) throw new Error('Failed to add memory');

      setNewMemory({ content: '', category: 'general', classification: 'public', metadata: '' });
      setShowAddMemory(false);
      fetchBrainData(); // Refresh data
    } catch (error) {
      setBrainState(prev => ({ ...prev, error: error.message }));
    }
  };

  const exportMemories = async () => {
    try {
      const response = await fetch(`${API_BASE}/brain/export`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          category: brainState.selectedCategory || null,
          classification: brainState.selectedClassification || null,
          include_signatures: true
        })
      });

      if (!response.ok) throw new Error('Export failed');

      const result = await response.json();
      
      // Create download link
      const blob = new Blob([JSON.stringify(result.export_data, null, 2)], { 
        type: 'application/json' 
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `brain_export_${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (error) {
      setBrainState(prev => ({ ...prev, error: error.message }));
    }
  };

  if (brainState.loading && !brainState.stats) {
    return (
      <div className="brain-console loading">
        <div className="loading-spinner">
          <div className="spinner-ring"></div>
          <p>Loading Brain Console...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="brain-console">
      <div className="brain-header">
        <div className="header-title">
          <h2>🧠 Sovereign Brain Console</h2>
          <p>Memory management and brain operations</p>
        </div>
        <div className="header-actions">
          <button 
            className="action-btn primary"
            onClick={() => setShowAddMemory(true)}
          >
            ➕ Add Memory
          </button>
          <button 
            className="action-btn secondary"
            onClick={exportMemories}
          >
            📤 Export
          </button>
          <button 
            className="action-btn refresh"
            onClick={fetchBrainData}
          >
            🔄 Refresh
          </button>
        </div>
      </div>

      {brainState.error && (
        <div className="error-banner">
          <span>❌ {brainState.error}</span>
          <button onClick={() => setBrainState(prev => ({ ...prev, error: null }))}>
            ✕
          </button>
        </div>
      )}

      {/* Brain Statistics */}
      {brainState.stats && (
        <div className="brain-stats">
          <div className="stat-card">
            <div className="stat-value">{brainState.stats.total_memories}</div>
            <div className="stat-label">Total Memories</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{brainState.stats.signed_memories}</div>
            <div className="stat-label">Signed</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{brainState.stats.unsigned_memories}</div>
            <div className="stat-label">Unsigned</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{Object.keys(brainState.stats.categories).length}</div>
            <div className="stat-label">Categories</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{brainState.stats.recent_activity}</div>
            <div className="stat-label">Recent Activity</div>
          </div>
        </div>
      )}

      {/* Search and Filters */}
      <div className="brain-search">
        <div className="search-row">
          <input
            type="text"
            placeholder="Search memories..."
            value={brainState.searchQuery}
            onChange={(e) => setBrainState(prev => ({ ...prev, searchQuery: e.target.value }))}
            className="search-input"
          />
          <select
            value={brainState.selectedCategory}
            onChange={(e) => setBrainState(prev => ({ ...prev, selectedCategory: e.target.value }))}
            className="filter-select"
          >
            <option value="">All Categories</option>
            {brainState.categories.map(cat => (
              <option key={cat.name} value={cat.name}>
                {cat.name} ({cat.count})
              </option>
            ))}
          </select>
          <select
            value={brainState.selectedClassification}
            onChange={(e) => setBrainState(prev => ({ ...prev, selectedClassification: e.target.value }))}
            className="filter-select"
          >
            <option value="">All Classifications</option>
            <option value="public">Public</option>
            <option value="private">Private</option>
            <option value="classified">Classified</option>
            <option value="operational">Operational</option>
          </select>
          <button onClick={searchMemories} className="search-btn">
            🔍 Search
          </button>
        </div>
      </div>

      {/* Memory List */}
      <div className="memory-list">
        {brainState.memories.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">🧠</div>
            <h3>No memories found</h3>
            <p>Add your first memory to the sovereign brain</p>
            <button 
              className="action-btn primary"
              onClick={() => setShowAddMemory(true)}
            >
              ➕ Add Memory
            </button>
          </div>
        ) : (
          <div className="memory-grid">
            {brainState.memories.map(memory => (
              <div key={memory.id} className="memory-card">
                <div className="memory-header">
                  <div className="memory-meta">
                    <span className="memory-id">#{memory.id}</span>
                    <span className={`memory-category ${memory.category}`}>
                      {memory.category}
                    </span>
                    <span className={`memory-classification ${memory.classification}`}>
                      {memory.classification}
                    </span>
                    {memory.signed && (
                      <span className="memory-signed" title="Cryptographically signed">
                        🔐
                      </span>
                    )}
                  </div>
                  <div className="memory-date">
                    {new Date(memory.created_at).toLocaleDateString()}
                  </div>
                </div>
                <div className="memory-content">
                  {memory.content.length > 200 
                    ? `${memory.content.substring(0, 200)}...`
                    : memory.content
                  }
                </div>
                {memory.metadata && Object.keys(memory.metadata).length > 0 && (
                  <div className="memory-metadata">
                    <strong>Metadata:</strong>
                    <pre>{JSON.stringify(memory.metadata, null, 2)}</pre>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Add Memory Modal */}
      {showAddMemory && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h3>➕ Add New Memory</h3>
              <button 
                className="modal-close"
                onClick={() => setShowAddMemory(false)}
              >
                ✕
              </button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label>Content *</label>
                <textarea
                  value={newMemory.content}
                  onChange={(e) => setNewMemory(prev => ({ ...prev, content: e.target.value }))}
                  placeholder="Enter memory content..."
                  required
                  rows={4}
                />
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>Category</label>
                  <select
                    value={newMemory.category}
                    onChange={(e) => setNewMemory(prev => ({ ...prev, category: e.target.value }))}
                  >
                    <option value="general">General</option>
                    <option value="operational">Operational</option>
                    <option value="strategic">Strategic</option>
                    <option value="tactical">Tactical</option>
                    <option value="intelligence">Intelligence</option>
                    <option value="archive">Archive</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>Classification</label>
                  <select
                    value={newMemory.classification}
                    onChange={(e) => setNewMemory(prev => ({ ...prev, classification: e.target.value }))}
                  >
                    <option value="public">Public</option>
                    <option value="private">Private</option>
                    <option value="classified">Classified</option>
                    <option value="operational">Operational</option>
                  </select>
                </div>
              </div>
              <div className="form-group">
                <label>Metadata (JSON)</label>
                <textarea
                  value={newMemory.metadata}
                  onChange={(e) => setNewMemory(prev => ({ ...prev, metadata: e.target.value }))}
                  placeholder='{"key": "value", "tags": ["example"]}'
                  rows={2}
                />
              </div>
            </div>
            <div className="modal-footer">
              <button 
                className="action-btn secondary"
                onClick={() => setShowAddMemory(false)}
              >
                Cancel
              </button>
              <button 
                className="action-btn primary"
                onClick={addMemory}
                disabled={!newMemory.content.trim()}
              >
                🔐 Add & Sign
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

/**
 * BrainConsole - Wrapped with Deployment Gate
 * Only reveals when backend systems are deployed
 */
const BrainConsole = () => {
  return (
    <SovereignRevealGate
      componentName="Brain Console"
      requiredSystems={['BRH Integration', 'Brain Memory System', 'Healing Net']}
    >
      <BrainConsoleCore />
    </SovereignRevealGate>
  );
};

export default BrainConsole;