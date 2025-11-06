/**
 * BRH (Bridge Runtime Handler) API Service
 * Handles all backend communication with error handling and retry logic
 */

import config from '../config';

const API_BASE = config.API_BASE_URL;

/**
 * BRH Service - Main backend integration service
 */
export const BRHService = {
  /**
   * Connect to BRH bridge and get status
   * @returns {Promise<Object>} Bridge status data
   */
  async connect() {
    try {
      const response = await fetch(`${API_BASE}/status`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('BRH Connection Failed:', error);
      return { 
        status: 'degraded', 
        agents: 0,
        error: error.message 
      };
    }
  },

  /**
   * Get bridge health status
   * @returns {Promise<Object>} Health data
   */
  async getHealth() {
    try {
      const response = await fetch(`${API_BASE}/health`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        throw new Error(`Health check failed: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Health Check Failed:', error);
      return { 
        status: 'unhealthy',
        error: error.message 
      };
    }
  },

  /**
   * Get full bridge status with components
   * @returns {Promise<Object>} Full health data
   */
  async getFullHealth() {
    try {
      const response = await fetch(`${API_BASE}/health/full`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        throw new Error(`Full health check failed: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Full Health Check Failed:', error);
      return {
        status: 'unhealthy',
        components: {},
        error: error.message
      };
    }
  },

  /**
   * Send a command to the BRH backend
   * @param {string} command - Command to execute
   * @param {Object} payload - Command payload
   * @returns {Promise<Object>} Command result
   */
  async sendCommand(command, payload = {}) {
    try {
      const response = await fetch(`${API_BASE}/command`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ command, ...payload }),
      });
      
      if (!response.ok) {
        throw new Error(`Command failed: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Command Execution Failed:', error);
      return {
        success: false,
        error: error.message
      };
    }
  },

  /**
   * Get agents online
   * @returns {Promise<Array>} List of online agents
   */
  async getAgents() {
    try {
      const response = await fetch(`${API_BASE}/agents`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        throw new Error(`Failed to fetch agents: ${response.status}`);
      }
      
      const data = await response.json();
      return Array.isArray(data) ? data : (data.agents || []);
    } catch (error) {
      console.error('Failed to fetch agents:', error);
      return [];
    }
  },

  /**
   * Get active missions
   * @param {Object} filters - Optional filters (captain, role, etc.)
   * @returns {Promise<Array>} List of missions
   */
  async getMissions(filters = {}) {
    try {
      const params = new URLSearchParams(filters);
      const query = params.toString() ? `?${params.toString()}` : '';
      
      const response = await fetch(`${API_BASE}/missions${query}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        throw new Error(`Failed to fetch missions: ${response.status}`);
      }
      
      const data = await response.json();
      return Array.isArray(data) ? data : (data.missions || []);
    } catch (error) {
      console.error('Failed to fetch missions:', error);
      return [];
    }
  },

  /**
   * Get fleet/armada status
   * @param {string} role - Optional role filter
   * @returns {Promise<Object>} Fleet status data
   */
  async getFleetStatus(role = null) {
    try {
      const params = new URLSearchParams();
      if (role) params.append('role', role);
      const query = params.toString() ? `?${params.toString()}` : '';
      
      const response = await fetch(`${API_BASE}/armada/status${query}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        throw new Error(`Failed to fetch fleet status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Failed to fetch fleet status:', error);
      return {
        status: 'unknown',
        ships: [],
        error: error.message
      };
    }
  },

  /**
   * Get vault logs
   * @param {Object} filters - Optional filters (level, limit, etc.)
   * @returns {Promise<Array>} List of logs
   */
  async getVaultLogs(filters = {}) {
    try {
      const params = new URLSearchParams(filters);
      const query = params.toString() ? `?${params.toString()}` : '';
      
      const response = await fetch(`${API_BASE}/vault/logs${query}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        throw new Error(`Failed to fetch vault logs: ${response.status}`);
      }
      
      const data = await response.json();
      return Array.isArray(data) ? data : (data.logs || []);
    } catch (error) {
      console.error('Failed to fetch vault logs:', error);
      return [];
    }
  },

  /**
   * Trigger self-heal operation
   * @returns {Promise<Object>} Heal result
   */
  async triggerSelfHeal() {
    try {
      const response = await fetch(`${API_BASE}/health/self-heal`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        throw new Error(`Self-heal failed: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Self-heal failed:', error);
      return {
        success: false,
        error: error.message
      };
    }
  },
};

export default BRHService;
