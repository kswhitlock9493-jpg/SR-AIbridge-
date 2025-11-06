/**
 * FleetStatus Component
 * Displays real-time fleet/agent monitoring with status indicators
 */

import { useState, useEffect } from 'react';
import { useRealtimeData } from '../hooks/useBRHConnection';

const FleetStatus = () => {
  const { data: agents, loading, error, lastUpdate, refetch } = useRealtimeData('agents', {
    refreshInterval: 5000, // Update every 5 seconds
  });

  const [filter, setFilter] = useState('all'); // all, online, offline

  // Filter agents based on status
  const filteredAgents = agents ? agents.filter(agent => {
    if (filter === 'all') return true;
    if (filter === 'online') return agent.status === 'online' || agent.status === 'active';
    if (filter === 'offline') return agent.status !== 'online' && agent.status !== 'active';
    return true;
  }) : [];

  // Calculate stats
  const totalAgents = agents ? agents.length : 0;
  const onlineAgents = agents ? agents.filter(a => a.status === 'online' || a.status === 'active').length : 0;
  const offlineAgents = totalAgents - onlineAgents;

  return (
    <div className="fleet-status-panel panel">
      <div className="panel-header">
        <h3>👥 Fleet Status</h3>
        <div className="fleet-stats">
          <span className="stat online">{onlineAgents} Online</span>
          <span className="stat offline">{offlineAgents} Offline</span>
          <span className="stat total">{totalAgents} Total</span>
        </div>
      </div>

      {error && (
        <div className="error-message">
          <span className="error-icon">⚠️</span>
          <span>Failed to load fleet data: {error}</span>
          <button onClick={refetch} className="retry-btn-small">Retry</button>
        </div>
      )}

      <div className="fleet-controls">
        <div className="filter-buttons">
          <button
            className={`filter-btn ${filter === 'all' ? 'active' : ''}`}
            onClick={() => setFilter('all')}
          >
            All
          </button>
          <button
            className={`filter-btn ${filter === 'online' ? 'active' : ''}`}
            onClick={() => setFilter('online')}
          >
            Online
          </button>
          <button
            className={`filter-btn ${filter === 'offline' ? 'active' : ''}`}
            onClick={() => setFilter('offline')}
          >
            Offline
          </button>
        </div>
        <div className="last-update">
          {lastUpdate && `Updated: ${lastUpdate.toLocaleTimeString()}`}
        </div>
      </div>

      <div className="fleet-grid">
        {loading && !agents && (
          <div className="loading-message">Loading fleet data...</div>
        )}

        {!loading && filteredAgents.length === 0 && (
          <div className="no-data">No agents found</div>
        )}

        {filteredAgents.map((agent) => (
          <div key={agent.id} className={`fleet-agent-card ${agent.status || 'offline'}`}>
            <div className="agent-header">
              <div className="agent-avatar">
                {agent.name ? agent.name.charAt(0).toUpperCase() : 'A'}
              </div>
              <div className="agent-info">
                <div className="agent-name">{agent.name || `Agent ${agent.id}`}</div>
                <div className="agent-role">{agent.role || 'Standard'}</div>
              </div>
              <div className={`status-badge ${agent.status || 'offline'}`}>
                <span className="status-dot"></span>
                <span className="status-text">{agent.status || 'offline'}</span>
              </div>
            </div>

            {agent.capabilities && agent.capabilities.length > 0 && (
              <div className="agent-capabilities">
                <div className="capabilities-label">Capabilities:</div>
                <div className="capabilities-list">
                  {agent.capabilities.slice(0, 3).map((cap, idx) => (
                    <span key={idx} className="capability-tag">{cap}</span>
                  ))}
                  {agent.capabilities.length > 3 && (
                    <span className="capability-tag more">+{agent.capabilities.length - 3}</span>
                  )}
                </div>
              </div>
            )}

            {agent.last_heartbeat && (
              <div className="agent-heartbeat">
                Last seen: {new Date(agent.last_heartbeat).toLocaleTimeString()}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default FleetStatus;
