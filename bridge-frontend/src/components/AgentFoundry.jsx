import { useState, useEffect, useCallback } from 'react';
import { apiClient } from '../api';
import { SovereignRevealGate } from './DeploymentGate.jsx';
import { RealAgentService } from '../services/true-data-revealer.js';
import { SilentFailureCapture } from '../services/silent-failure-capture.js';

/**
 * Agent Foundry - Comprehensive Agent Creation and Management
 * Features invisible Indoctrination Engine integration
 * No separate tab needed - indoctrination is seamlessly integrated
 * 
 * DEPLOYMENT GATE: Only reveals real functionality when backend is deployed
 */
const AgentFoundryCore = () => {
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showForgeForm, setShowForgeForm] = useState(false);
  
  // New agent blueprint
  const [newAgent, setNewAgent] = useState({
    name: '',
    role: '',
    specialties: '',
    doctrineLevel: 'standard', // Automatic indoctrination level
    autoIndoctrinate: true // Invisible indoctrination on creation
  });

  // Quality assurance metrics
  const [qaMetrics, setQaMetrics] = useState({
    total: 0,
    certified: 0,
    pending: 0,
    revoked: 0
  });

  // Fetch agents from Indoctrination Engine
  const fetchAgents = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Use RealAgentService for deployment-aware data fetching
      const agentList = await RealAgentService.getAgents();
      setAgents(agentList);
      
      // Calculate QA metrics
      const metrics = {
        total: agentList.length,
        certified: agentList.filter(a => a.certified || a.status === 'active').length,
        pending: agentList.filter(a => a.status === 'onboarding' || a.status === 'pending').length,
        revoked: agentList.filter(a => a.status === 'revoked').length
      };
      setQaMetrics(metrics);
      
      // Record successful health check
      SilentFailureCapture.recordHealthCheck('agent-foundry-indoctrination', true);
    } catch (err) {
      console.error('Failed to fetch agents:', err);
      setError('Failed to load agents: ' + err.message);
      
      // Record failure
      SilentFailureCapture.recordHealthCheck('agent-foundry-indoctrination', false, err);
      setError('Failed to load agents: ' + err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAgents();
  }, [fetchAgents]);

  // Forge new agent with automatic indoctrination
  const handleForgeAgent = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      setError(null);

      // Parse specialties
      const specialties = newAgent.specialties
        .split(',')
        .map(s => s.trim())
        .filter(s => s.length > 0);

      // Create agent through Indoctrination Engine
      const response = await apiClient.post('/engines/indoctrination/onboard', {
        name: newAgent.name,
        role: newAgent.role,
        specialties
      });

      // INVISIBLE INDOCTRINATION: Auto-certify if enabled
      if (newAgent.autoIndoctrinate && response.id) {
        try {
          await apiClient.post(`/engines/indoctrination/${response.id}/certify`, {
            doctrine: newAgent.doctrineLevel
          });
          console.log(`[AgentFoundry] Auto-indoctrination completed for ${newAgent.name}`);
        } catch (certError) {
          console.warn('[AgentFoundry] Auto-indoctrination failed, manual certification required:', certError);
        }
      }

      // Reset form
      setNewAgent({
        name: '',
        role: '',
        specialties: '',
        doctrineLevel: 'standard',
        autoIndoctrinate: true
      });
      setShowForgeForm(false);

      // Refresh agent list
      await fetchAgents();
    } catch (err) {
      console.error('Failed to forge agent:', err);
      setError('Failed to forge agent: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  // Manual certification for existing agents
  const handleCertifyAgent = async (agentId) => {
    try {
      await apiClient.post(`/engines/indoctrination/${agentId}/certify`, {
        doctrine: 'standard'
      });
      await fetchAgents();
    } catch (err) {
      console.error('Failed to certify agent:', err);
      setError('Failed to certify agent: ' + err.message);
    }
  };

  // Revoke agent
  const handleRevokeAgent = async (agentId) => {
    if (!confirm('⚠️ This will revoke the agent\'s certification. Continue?')) {
      return;
    }

    try {
      await apiClient.post(`/engines/indoctrination/${agentId}/revoke`, {
        reason: 'Manual revocation from Agent Foundry'
      });
      await fetchAgents();
    } catch (err) {
      console.error('Failed to revoke agent:', err);
      setError('Failed to revoke agent: ' + err.message);
    }
  };

  const getStatusIcon = (agent) => {
    if (agent.certified || agent.status === 'active') return '✅';
    if (agent.status === 'revoked') return '❌';
    if (agent.status === 'onboarding' || agent.status === 'pending') return '⏳';
    return '🔄';
  };

  const getStatusColor = (agent) => {
    if (agent.certified || agent.status === 'active') return '#4CAF50';
    if (agent.status === 'revoked') return '#f44336';
    if (agent.status === 'onboarding' || agent.status === 'pending') return '#ff9800';
    return '#2196F3';
  };

  return (
    <div className="agent-foundry panel">
      <div className="panel-header">
        <h2>🛠️ Agent Foundry</h2>
        <p className="panel-subtitle">
          Forge and manage autonomous agents with invisible indoctrination
        </p>
      </div>

      {error && (
        <div className="alert alert-error">
          <span>⚠️</span>
          <span>{error}</span>
        </div>
      )}

      {/* Quality Assurance Sanctum - Metrics Overview */}
      <div className="qa-sanctum" style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
        gap: '12px',
        marginBottom: '20px'
      }}>
        <div className="metric-card" style={{
          padding: '16px',
          backgroundColor: 'rgba(76, 175, 80, 0.1)',
          borderRadius: '8px',
          border: '1px solid rgba(76, 175, 80, 0.3)'
        }}>
          <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#4CAF50' }}>
            {qaMetrics.certified}
          </div>
          <div style={{ fontSize: '12px', color: '#666' }}>Certified Agents</div>
        </div>

        <div className="metric-card" style={{
          padding: '16px',
          backgroundColor: 'rgba(255, 152, 0, 0.1)',
          borderRadius: '8px',
          border: '1px solid rgba(255, 152, 0, 0.3)'
        }}>
          <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#ff9800' }}>
            {qaMetrics.pending}
          </div>
          <div style={{ fontSize: '12px', color: '#666' }}>Pending</div>
        </div>

        <div className="metric-card" style={{
          padding: '16px',
          backgroundColor: 'rgba(33, 150, 243, 0.1)',
          borderRadius: '8px',
          border: '1px solid rgba(33, 150, 243, 0.3)'
        }}>
          <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#2196F3' }}>
            {qaMetrics.total}
          </div>
          <div style={{ fontSize: '12px', color: '#666' }}>Total Agents</div>
        </div>

        {qaMetrics.revoked > 0 && (
          <div className="metric-card" style={{
            padding: '16px',
            backgroundColor: 'rgba(244, 67, 54, 0.1)',
            borderRadius: '8px',
            border: '1px solid rgba(244, 67, 54, 0.3)'
          }}>
            <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#f44336' }}>
              {qaMetrics.revoked}
            </div>
            <div style={{ fontSize: '12px', color: '#666' }}>Revoked</div>
          </div>
        )}
      </div>

      {/* Forging Chamber - Agent Creation */}
      <div className="forging-chamber" style={{ marginBottom: '20px' }}>
        <button
          onClick={() => setShowForgeForm(!showForgeForm)}
          className="btn btn-primary"
          style={{
            padding: '10px 20px',
            backgroundColor: '#2196F3',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            fontSize: '14px',
            fontWeight: 'bold'
          }}
        >
          {showForgeForm ? '❌ Cancel' : '⚒️ Forge New Agent'}
        </button>

        {showForgeForm && (
          <form onSubmit={handleForgeAgent} style={{
            marginTop: '16px',
            padding: '20px',
            backgroundColor: 'rgba(33, 150, 243, 0.05)',
            borderRadius: '8px',
            border: '1px solid rgba(33, 150, 243, 0.2)'
          }}>
            <h3 style={{ marginTop: 0 }}>🏗️ Agent Blueprint Designer</h3>
            
            <div style={{ display: 'grid', gap: '12px' }}>
              <div>
                <label style={{ display: 'block', marginBottom: '4px', fontWeight: 'bold' }}>
                  Agent Name *
                </label>
                <input
                  type="text"
                  value={newAgent.name}
                  onChange={(e) => setNewAgent({ ...newAgent, name: e.target.value })}
                  placeholder="e.g., Alpha-01"
                  required
                  style={{
                    width: '100%',
                    padding: '8px',
                    borderRadius: '4px',
                    border: '1px solid #ddd'
                  }}
                />
              </div>

              <div>
                <label style={{ display: 'block', marginBottom: '4px', fontWeight: 'bold' }}>
                  Role *
                </label>
                <input
                  type="text"
                  value={newAgent.role}
                  onChange={(e) => setNewAgent({ ...newAgent, role: e.target.value })}
                  placeholder="e.g., Combat, Support, Intelligence"
                  required
                  style={{
                    width: '100%',
                    padding: '8px',
                    borderRadius: '4px',
                    border: '1px solid #ddd'
                  }}
                />
              </div>

              <div>
                <label style={{ display: 'block', marginBottom: '4px', fontWeight: 'bold' }}>
                  Specialties (comma-separated)
                </label>
                <input
                  type="text"
                  value={newAgent.specialties}
                  onChange={(e) => setNewAgent({ ...newAgent, specialties: e.target.value })}
                  placeholder="e.g., Navigation, Tactics, Reconnaissance"
                  style={{
                    width: '100%',
                    padding: '8px',
                    borderRadius: '4px',
                    border: '1px solid #ddd'
                  }}
                />
              </div>

              <div>
                <label style={{ display: 'block', marginBottom: '4px', fontWeight: 'bold' }}>
                  Doctrine Level
                </label>
                <select
                  value={newAgent.doctrineLevel}
                  onChange={(e) => setNewAgent({ ...newAgent, doctrineLevel: e.target.value })}
                  style={{
                    width: '100%',
                    padding: '8px',
                    borderRadius: '4px',
                    border: '1px solid #ddd'
                  }}
                >
                  <option value="basic">Basic</option>
                  <option value="standard">Standard</option>
                  <option value="advanced">Advanced</option>
                  <option value="elite">Elite</option>
                </select>
              </div>

              <div style={{
                padding: '12px',
                backgroundColor: 'rgba(76, 175, 80, 0.1)',
                borderRadius: '4px',
                border: '1px solid rgba(76, 175, 80, 0.3)'
              }}>
                <label style={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}>
                  <input
                    type="checkbox"
                    checked={newAgent.autoIndoctrinate}
                    onChange={(e) => setNewAgent({ ...newAgent, autoIndoctrinate: e.target.checked })}
                    style={{ marginRight: '8px' }}
                  />
                  <span style={{ fontWeight: 'bold' }}>
                    ⚔️ Auto-Indoctrination (Invisible Engine)
                  </span>
                </label>
                <p style={{ margin: '4px 0 0 24px', fontSize: '12px', color: '#666' }}>
                  Automatically certify agent with doctrine on creation
                </p>
              </div>
            </div>

            <div style={{ marginTop: '16px', display: 'flex', gap: '12px' }}>
              <button
                type="submit"
                disabled={loading}
                style={{
                  padding: '10px 20px',
                  backgroundColor: '#4CAF50',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: loading ? 'not-allowed' : 'pointer',
                  fontSize: '14px',
                  fontWeight: 'bold',
                  opacity: loading ? 0.6 : 1
                }}
              >
                {loading ? '⚒️ Forging...' : '✨ Forge Agent'}
              </button>
            </div>
          </form>
        )}
      </div>

      {/* Agent Registry */}
      <div className="agent-registry">
        <h3>📋 Agent Registry</h3>
        
        {loading && agents.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '20px', color: '#666' }}>
            Loading agents...
          </div>
        ) : agents.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '20px', color: '#666' }}>
            No agents forged yet. Create your first agent above!
          </div>
        ) : (
          <div style={{ display: 'grid', gap: '12px' }}>
            {agents.map(agent => (
              <div
                key={agent.id}
                style={{
                  padding: '16px',
                  backgroundColor: 'rgba(255, 255, 255, 0.05)',
                  borderRadius: '8px',
                  border: `2px solid ${getStatusColor(agent)}`,
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center'
                }}
              >
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                    <span style={{ fontSize: '20px' }}>{getStatusIcon(agent)}</span>
                    <strong style={{ fontSize: '16px' }}>{agent.name}</strong>
                    <span style={{
                      padding: '2px 8px',
                      backgroundColor: getStatusColor(agent),
                      color: 'white',
                      borderRadius: '4px',
                      fontSize: '11px',
                      fontWeight: 'bold'
                    }}>
                      {agent.status || (agent.certified ? 'ACTIVE' : 'PENDING')}
                    </span>
                  </div>
                  <div style={{ fontSize: '14px', color: '#666' }}>
                    Role: {agent.role}
                  </div>
                  {agent.specialties && agent.specialties.length > 0 && (
                    <div style={{ fontSize: '12px', color: '#999', marginTop: '4px' }}>
                      Specialties: {agent.specialties.join(', ')}
                    </div>
                  )}
                </div>

                <div style={{ display: 'flex', gap: '8px' }}>
                  {!agent.certified && agent.status !== 'active' && (
                    <button
                      onClick={() => handleCertifyAgent(agent.id)}
                      style={{
                        padding: '6px 12px',
                        backgroundColor: '#4CAF50',
                        color: 'white',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: 'pointer',
                        fontSize: '12px'
                      }}
                    >
                      ✅ Certify
                    </button>
                  )}
                  
                  {(agent.certified || agent.status === 'active') && (
                    <button
                      onClick={() => handleRevokeAgent(agent.id)}
                      style={{
                        padding: '6px 12px',
                        backgroundColor: '#f44336',
                        color: 'white',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: 'pointer',
                        fontSize: '12px'
                      }}
                    >
                      🚫 Revoke
                    </button>
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

/**
 * AgentFoundry - Wrapped with Deployment Gate
 * Only reveals when backend systems are deployed
 */
const AgentFoundry = () => {
  return (
    <SovereignRevealGate
      componentName="Agent Foundry"
      requiredSystems={['BRH Integration', 'Indoctrination Engine', 'Crypto System']}
    >
      <AgentFoundryCore />
    </SovereignRevealGate>
  );
};

export default AgentFoundry;
