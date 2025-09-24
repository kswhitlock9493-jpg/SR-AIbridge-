import React, { useState, useCallback } from 'react';
import { getAgents, createAgent, removeAgent } from '../api';
import { usePolling } from '../hooks/usePolling';

const Agents = () => {
  const [agents, setAgents] = useState([]);
  const [showRegisterForm, setShowRegisterForm] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    endpoint: '',
    capabilities: []
  });
  const [capabilityInput, setCapabilityInput] = useState('');

  // Fetch agents with 30s polling for live registry
  const fetchAgents = useCallback(async () => {
    const data = await getAgents();
    setAgents(data);
    return data;
  }, []);

  const { loading, error, refresh } = usePolling(fetchAgents, {
    interval: 30000, // 30 seconds for agent registry updates
    immediate: true,
    debounceDelay: 200
  });

  const handleRegisterAgent = async (e) => {
    e.preventDefault();
    try {
      await createAgent({
        name: formData.name,
        endpoint: formData.endpoint,
        capabilities: formData.capabilities
      });
      
      setFormData({ name: '', endpoint: '', capabilities: [] });
      setCapabilityInput('');
      setShowRegisterForm(false);
      refresh();
    } catch (error) {
      console.error('Failed to register agent:', error);
    }
  };

  const handleRemoveAgent = async (agentId) => {
    if (window.confirm('Are you sure you want to remove this agent?')) {
      try {
        await removeAgent(agentId);
        refresh();
      } catch (error) {
        console.error('Failed to remove agent:', error);
      }
    }
  };

  const addCapability = () => {
    if (capabilityInput.trim() && !formData.capabilities.includes(capabilityInput.trim())) {
      setFormData({
        ...formData,
        capabilities: [...formData.capabilities, capabilityInput.trim()]
      });
      setCapabilityInput('');
    }
  };

  const removeCapability = (capability) => {
    setFormData({
      ...formData,
      capabilities: formData.capabilities.filter(cap => cap !== capability)
    });
  };

  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'online': return '#00ff00';
      case 'offline': return '#ff4444';
      case 'busy': return '#ffaa00';
      case 'maintenance': return '#888';
      default: return '#888';
    }
  };

  const formatTimestamp = (timestamp) => {
    if (!timestamp) return 'Never';
    return new Date(timestamp).toLocaleString();
  };

  const getAgentStats = () => {
    const total = agents.length;
    const online = agents.filter(agent => agent.status === 'online').length;
    const offline = agents.filter(agent => agent.status === 'offline').length;
    const busy = agents.filter(agent => agent.status === 'busy').length;
    
    return { total, online, offline, busy };
  };

  if (loading) {
    return (
      <div className="agents">
        <h2>🤖 Agent Registry</h2>
        <div className="loading">Loading agent registry...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="agents">
        <h2>🤖 Agent Registry</h2>
        <div className="error">Error loading agents: {error}</div>
        <button onClick={refresh} className="retry-button">Retry</button>
      </div>
    );
  }

  const stats = getAgentStats();

  return (
    <div className="agents">
      <div className="header">
        <h2>🤖 Agent Registry</h2>
        <div className="header-actions">
          <button onClick={refresh} className="refresh-button">🔄 Refresh</button>
          <button 
            onClick={() => setShowRegisterForm(!showRegisterForm)} 
            className="register-button"
          >
            {showRegisterForm ? '❌ Cancel' : '➕ Register Agent'}
          </button>
        </div>
      </div>

      <div className="agent-stats">
        <div className="stat-card">
          <div className="stat-number">{stats.total}</div>
          <div className="stat-label">Total Agents</div>
        </div>
        <div className="stat-card online">
          <div className="stat-number">{stats.online}</div>
          <div className="stat-label">Online</div>
        </div>
        <div className="stat-card offline">
          <div className="stat-number">{stats.offline}</div>
          <div className="stat-label">Offline</div>
        </div>
        <div className="stat-card busy">
          <div className="stat-number">{stats.busy}</div>
          <div className="stat-label">Busy</div>
        </div>
      </div>

      {showRegisterForm && (
        <form onSubmit={handleRegisterAgent} className="register-agent-form">
          <h3>Register New Agent</h3>
          <div className="form-row">
            <label>
              Agent Name:
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
                placeholder="e.g., Alpha-7"
              />
            </label>
          </div>
          <div className="form-row">
            <label>
              Endpoint URL:
              <input
                type="url"
                value={formData.endpoint}
                onChange={(e) => setFormData({ ...formData, endpoint: e.target.value })}
                required
                placeholder="e.g., https://agent.example.com/api"
              />
            </label>
          </div>
          <div className="form-row">
            <label>
              Capabilities:
              <div className="capability-input">
                <input
                  type="text"
                  value={capabilityInput}
                  onChange={(e) => setCapabilityInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addCapability())}
                  placeholder="Enter capability and press Enter"
                />
                <button type="button" onClick={addCapability} className="add-capability-btn">
                  Add
                </button>
              </div>
              <div className="capabilities-list">
                {formData.capabilities.map((capability, index) => (
                  <span key={index} className="capability-tag">
                    {capability}
                    <button 
                      type="button" 
                      onClick={() => removeCapability(capability)}
                      className="remove-capability"
                    >
                      ×
                    </button>
                  </span>
                ))}
              </div>
            </label>
          </div>
          <div className="form-actions">
            <button type="submit" className="submit-button">Register Agent</button>
            <button type="button" onClick={() => setShowRegisterForm(false)} className="cancel-button">
              Cancel
            </button>
          </div>
        </form>
      )}

      <div className="agents-container">
        {agents.length === 0 ? (
          <div className="no-agents">No agents registered</div>
        ) : (
          <div className="agents-grid">
            {agents.map((agent) => (
              <div key={agent.id} className="agent-card">
                <div className="agent-header">
                  <h3 className="agent-name">{agent.name}</h3>
                  <span 
                    className="status-indicator" 
                    style={{ color: getStatusColor(agent.status) }}
                  >
                    ● {agent.status?.toUpperCase()}
                  </span>
                </div>
                
                <div className="agent-details">
                  <div className="detail-row">
                    <span className="label">Endpoint:</span>
                    <span className="value endpoint">{agent.endpoint}</span>
                  </div>
                  <div className="detail-row">
                    <span className="label">Agent ID:</span>
                    <span className="value agent-id">{agent.id}</span>
                  </div>
                  <div className="detail-row">
                    <span className="label">Last Heartbeat:</span>
                    <span className="value">{formatTimestamp(agent.last_heartbeat)}</span>
                  </div>
                  <div className="detail-row">
                    <span className="label">Created:</span>
                    <span className="value">{formatTimestamp(agent.created_at)}</span>
                  </div>
                </div>

                {agent.capabilities && agent.capabilities.length > 0 && (
                  <div className="capabilities">
                    <div className="label">Capabilities:</div>
                    <div className="capabilities-list">
                      {agent.capabilities.map((capability, index) => (
                        <span key={index} className="capability-tag">
                          {typeof capability === 'string' ? capability : capability.name || 'Unknown'}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                <div className="agent-actions">
                  <button 
                    onClick={() => handleRemoveAgent(agent.id)}
                    className="remove-button"
                    title="Remove Agent"
                  >
                    🗑️ Remove
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Agents;