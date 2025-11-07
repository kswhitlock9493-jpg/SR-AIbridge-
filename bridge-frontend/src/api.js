import config from './config';
import { APIGuardian, CircuitBreaker } from './services/healing-net';

const API_BASE_URL = config.API_BASE_URL;

// Circuit breakers for different service categories
const circuitBreakers = {
  missions: new CircuitBreaker('missions', { failureThreshold: 5, resetTimeout: 60000 }),
  brain: new CircuitBreaker('brain', { failureThreshold: 5, resetTimeout: 60000 }),
  custody: new CircuitBreaker('custody', { failureThreshold: 5, resetTimeout: 60000 }),
  vault: new CircuitBreaker('vault', { failureThreshold: 5, resetTimeout: 60000 }),
  engines: new CircuitBreaker('engines', { failureThreshold: 5, resetTimeout: 60000 })
};

// Map endpoint paths to Netlify Function names (when using Netlify Functions)
const NETLIFY_ENDPOINT_MAP = {
  '/status': '/api-status',
  '/agents': '/api-agents',
  '/missions': '/api-missions',
  '/vault/logs': '/api-vault-logs',
  '/armada/status': '/api-armada-status',
  '/health': '/api-system-health',
  '/activity': '/api-activity'
};

// Enhanced API client with retry logic and robust error handling
class APIClient {
  constructor(baseURL, options = {}) {
    this.baseURL = baseURL;
    this.defaultTimeout = options.timeout || 10000;
    this.maxRetries = options.maxRetries || 3;
    this.baseRetryDelay = options.baseRetryDelay || 1000;
    this.isNetlifyFunctions = baseURL.includes('/.netlify/functions');
  }

  // Transform endpoint for Netlify Functions if needed
  transformEndpoint(endpoint) {
    if (!this.isNetlifyFunctions) {
      return endpoint;
    }
    
    // For Netlify Functions, map the endpoint to the function name
    // First check exact matches
    if (NETLIFY_ENDPOINT_MAP[endpoint]) {
      return NETLIFY_ENDPOINT_MAP[endpoint];
    }
    
    // Check for partial matches (e.g., /missions?captain=x -> /api-missions?captain=x)
    for (const [key, value] of Object.entries(NETLIFY_ENDPOINT_MAP)) {
      if (endpoint.startsWith(key)) {
        return endpoint.replace(key, value);
      }
    }
    
    // Default: prepend "api" and replace slashes with dashes
    // e.g., /users/profile -> /api-users-profile
    return `/api${endpoint.replace(/\//g, '-')}`;
  }

  async request(endpoint, options = {}) {
    // Transform endpoint if using Netlify Functions
    const transformedEndpoint = this.transformEndpoint(endpoint);
    
    // Determine which circuit breaker to use based on endpoint
    let circuitBreaker = null;
    if (transformedEndpoint.includes('/missions')) {
      circuitBreaker = circuitBreakers.missions;
    } else if (transformedEndpoint.includes('/brain')) {
      circuitBreaker = circuitBreakers.brain;
    } else if (transformedEndpoint.includes('/custody')) {
      circuitBreaker = circuitBreakers.custody;
    } else if (transformedEndpoint.includes('/vault')) {
      circuitBreaker = circuitBreakers.vault;
    } else if (transformedEndpoint.includes('/engines')) {
      circuitBreaker = circuitBreakers.engines;
    }

    const executeRequest = async () => {
      return await APIGuardian.safeFetch(transformedEndpoint, {
        ...options,
        baseURL: this.baseURL,
        timeout: options.timeout || this.defaultTimeout,
        retries: options.retries || this.maxRetries,
        fallbackOnError: options.fallbackOnError !== false
      });
    };

    // Execute with circuit breaker if available
    if (circuitBreaker) {
      try {
        return await circuitBreaker.execute(executeRequest);
      } catch (error) {
        // Circuit breaker is open, use fallback
        if (error.name === 'HealingNetException' && error.message.includes('Circuit breaker')) {
          console.warn('[API] Circuit breaker triggered, using fallback');
          const { UmbraLattice } = await import('./services/healing-net');
          return UmbraLattice.getFallbackData(transformedEndpoint);
        }
        throw error;
      }
    }

    // No circuit breaker, execute directly
    return executeRequest();
  }

  // HTTP method helpers
  async get(endpoint, options = {}) {
    return this.request(endpoint, { ...options, method: 'GET' });
  }

  async post(endpoint, data, options = {}) {
    return this.request(endpoint, { ...options, method: 'POST', body: data });
  }

  async patch(endpoint, data, options = {}) {
    return this.request(endpoint, { ...options, method: 'PATCH', body: data });
  }

  async delete(endpoint, options = {}) {
    return this.request(endpoint, { ...options, method: 'DELETE' });
  }
}

// Create API client instance
const apiClient = new APIClient(API_BASE_URL);

// === Core Status ===
export async function getStatus() {
  return apiClient.get('/status');
}

// === Agents ===
export async function getAgents() {
  return apiClient.get('/agents');
}

export async function createAgent(agent) {
  return apiClient.post('/agents', agent);
}

export async function removeAgent(agentId) {
  return apiClient.delete(`/agents/${agentId}`);
}

// === Missions ===
export async function getMissions(captain = null, role = null) {
  const params = new URLSearchParams();
  if (captain) params.append('captain', captain);
  if (role) params.append('role', role);
  const query = params.toString() ? `?${params.toString()}` : '';
  return apiClient.get(`/missions${query}`);
}

export async function createMission(mission) {
  return apiClient.post('/missions', mission);
}

export async function assignAgentToMission(missionId, agentId) {
  return apiClient.post(`/missions/${missionId}/assign`, { agent_id: agentId });
}

export async function updateMissionStatus(missionId, status, extraData = {}) {
  const updates = { ...extraData };
  if (status !== null && status !== undefined) {
    updates.status = status;
  }
  return apiClient.patch(`/missions/${missionId}`, updates);
}

// === Vault Logs / Doctrine ===
export async function getVaultLogs() {
  return apiClient.get('/vault/logs');
}

export async function addVaultLog(log) {
  return apiClient.post('/vault/logs', log);
}

// === Captain-to-Captain Chat ===
export async function getCaptainMessages() {
  return apiClient.get('/captains/messages');
}

export async function sendCaptainMessage(message) {
  return apiClient.post('/captains/send', message);
}

// === Armada/Fleet ===
export async function getArmadaStatus(role = null) {
  const params = new URLSearchParams();
  if (role) params.append('role', role);
  const query = params.toString() ? `?${params.toString()}` : '';
  return apiClient.get(`/armada/status${query}`);
}

export async function getFleetData(role = null) {
  // Updated to use the new /fleet endpoint with optional role filter
  const params = new URLSearchParams();
  if (role) params.append('role', role);
  const query = params.toString() ? `?${params.toString()}` : '';
  return apiClient.get(`/fleet${query}`);
}

export async function getFleetStatus(role = null) {
  // Alias for getFleetData to match /fleet/status endpoint requirement
  return getFleetData(role);
}

// === Activity ===
export async function getActivity() {
  return apiClient.get('/activity');
}

// === Additional Endpoints ===
export async function getLogs() {
  return apiClient.get('/logs');
}

export async function getSystemHealth() {
  return apiClient.get('/health');
}

export async function getSystemHealthFull() {
  return apiClient.get('/health/full');
}

// === System Health & Self-Heal (Enhanced) ===
export async function triggerSystemSelfHeal() {
  return apiClient.post('/health/self-heal');
}

// === Utilities ===
export async function reseedDemoData() {
  return apiClient.post('/reseed');
}

// === Error Recovery ===
export async function runSelfTest() {
  // Updated to call /health/full for comprehensive system checks
  return apiClient.get('/health/full');
}

export async function runSelfRepair() {
  return apiClient.post('/health/self-heal');  // Updated to use the correct endpoint
}

export async function getSystemMetrics() {
  return apiClient.get('/system/metrics');
}

// === Guardian System ===
export async function getGuardianStatus() {
  return apiClient.get('/guardian/status');
}

export async function runGuardianSelftest() {
  return apiClient.post('/guardian/selftest');
}

export async function activateGuardian() {
  return apiClient.post('/guardian/activate');
}

// === Chat Integration ===
export async function getChatMessages() {
  return apiClient.get('/chat/messages');
}

export async function postChatMessage(author, message) {
  return apiClient.post('/chat/messages', { author, message });
}

// === Centralized fetchData function for all backend endpoints ===
export async function fetchData(endpoint) {
  /**
   * Centralized function for fetching data from backend endpoints
   * All panel components should use this for backend data endpoints:
   * /status, /agents, /missions, /vault/logs, /captains/messages, /fleet/status, /armada/status, /health
   */
  return apiClient.get(endpoint);
}

// Export the API client for advanced usage
export { apiClient };