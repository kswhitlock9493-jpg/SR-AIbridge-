import React, { useState, useCallback } from 'react';
import { getMissions, getAgents, createMission, assignAgentToMission, updateMissionStatus } from '../api';
import { usePolling } from '../hooks/usePolling';

const MissionControls = ({ onMissionDispatch }) => {
  const [missions, setMissions] = useState([]);
  const [agents, setAgents] = useState([]);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    priority: 'normal'
  });

  // Fetch missions with 30s polling
  const fetchMissions = useCallback(async () => {
    const data = await getMissions();
    setMissions(data);
    return data;
  }, []);

  // Fetch agents with 30s polling
  const fetchAgents = useCallback(async () => {
    const data = await getAgents();
    setAgents(data);
    return data;
  }, []);

  const { loading: missionsLoading, error: missionsError, refresh: refreshMissions } = usePolling(fetchMissions, {
    interval: 30000,
    immediate: true,
    debounceDelay: 200
  });

  const { loading: agentsLoading, error: agentsError, refresh: refreshAgents } = usePolling(fetchAgents, {
    interval: 30000,
    immediate: true,
    debounceDelay: 200
  });

  const handleCreateMission = async (e) => {
    e.preventDefault();
    try {
      const newMission = await createMission({
        title: formData.title,
        description: formData.description,
        priority: formData.priority,
        status: 'planning'
      });
      
      setFormData({ title: '', description: '', priority: 'normal' });
      setShowCreateForm(false);
      refreshMissions();
      
      // Notify parent component of new mission
      if (onMissionDispatch) {
        onMissionDispatch(newMission);
      }
    } catch (error) {
      console.error('Failed to create mission:', error);
    }
  };

  const handleAssignAgent = async (missionId, agentId) => {
    try {
      await assignAgentToMission(missionId, agentId);
      refreshMissions();
    } catch (error) {
      console.error('Failed to assign agent:', error);
    }
  };

  const handleStatusChange = async (missionId, newStatus) => {
    try {
      await updateMissionStatus(missionId, newStatus);
      refreshMissions();
      
      // Notify parent component of mission status change
      if (onMissionDispatch) {
        onMissionDispatch({ id: missionId, status: newStatus });
      }
    } catch (error) {
      console.error('Failed to update mission status:', error);
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

  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'active': return '#00ff00';
      case 'completed': return '#00aaff';
      case 'planning': return '#ffaa00';
      case 'failed': return '#ff4444';
      default: return '#888';
    }
  };

  const getAvailableAgents = () => {
    return agents.filter(agent => agent.status === 'online');
  };

  if (missionsLoading || agentsLoading) {
    return (
      <div className="mission-controls">
        <h2>🎯 Mission Controls</h2>
        <div className="loading">Loading mission controls...</div>
      </div>
    );
  }

  if (missionsError || agentsError) {
    return (
      <div className="mission-controls">
        <h2>🎯 Mission Controls</h2>
        <div className="error">
          Error loading data: {missionsError || agentsError}
        </div>
        <button onClick={() => { refreshMissions(); refreshAgents(); }} className="retry-button">
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="mission-controls">
      <div className="header">
        <h2>🎯 Mission Controls</h2>
        <div className="header-actions">
          <button onClick={() => { refreshMissions(); refreshAgents(); }} className="refresh-button">
            🔄 Refresh
          </button>
          <button 
            onClick={() => setShowCreateForm(!showCreateForm)} 
            className="create-button"
          >
            {showCreateForm ? '❌ Cancel' : '➕ New Mission'}
          </button>
        </div>
      </div>

      {showCreateForm && (
        <form onSubmit={handleCreateMission} className="create-mission-form">
          <h3>Create New Mission</h3>
          <div className="form-row">
            <label>
              Title:
              <input
                type="text"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                required
              />
            </label>
          </div>
          <div className="form-row">
            <label>
              Description:
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                required
                rows="3"
              />
            </label>
          </div>
          <div className="form-row">
            <label>
              Priority:
              <select
                value={formData.priority}
                onChange={(e) => setFormData({ ...formData, priority: e.target.value })}
              >
                <option value="low">Low</option>
                <option value="normal">Normal</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
            </label>
          </div>
          <div className="form-actions">
            <button type="submit" className="submit-button">Create Mission</button>
            <button type="button" onClick={() => setShowCreateForm(false)} className="cancel-button">
              Cancel
            </button>
          </div>
        </form>
      )}

      <div className="missions-control-panel">
        <h3>Active Mission Control</h3>
        {missions.length === 0 ? (
          <div className="no-missions">No missions available</div>
        ) : (
          <div className="missions-grid">
            {missions.filter(mission => mission.status !== 'completed').map((mission) => (
              <div key={mission.id} className="mission-control-card">
                <div className="mission-header">
                  <h4>{mission.title}</h4>
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
                      {mission.priority?.toUpperCase()}
                    </span>
                  </div>
                </div>
                
                <div className="mission-description">{mission.description}</div>
                
                <div className="mission-controls">
                  <div className="status-controls">
                    <label>Status:</label>
                    <select
                      value={mission.status}
                      onChange={(e) => handleStatusChange(mission.id, e.target.value)}
                    >
                      <option value="planning">Planning</option>
                      <option value="active">Active</option>
                      <option value="completed">Completed</option>
                      <option value="failed">Failed</option>
                    </select>
                  </div>
                  
                  <div className="agent-assignment">
                    <label>Assign Agent:</label>
                    <select
                      onChange={(e) => {
                        if (e.target.value) {
                          handleAssignAgent(mission.id, parseInt(e.target.value));
                          e.target.value = '';
                        }
                      }}
                      defaultValue=""
                    >
                      <option value="">Select Agent...</option>
                      {getAvailableAgents().map((agent) => (
                        <option key={agent.id} value={agent.id}>
                          {agent.name} ({agent.status})
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="agent-status-panel">
        <h3>Available Agents ({getAvailableAgents().length})</h3>
        <div className="agents-status-grid">
          {getAvailableAgents().slice(0, 6).map((agent) => (
            <div key={agent.id} className="agent-status-card">
              <div className="agent-name">{agent.name}</div>
              <div className="agent-status" style={{ color: '#00ff00' }}>
                ● {agent.status?.toUpperCase()}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default MissionControls;