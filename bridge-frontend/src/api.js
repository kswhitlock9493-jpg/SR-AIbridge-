import config from './config';

const API_BASE_URL = config.API_BASE_URL;

// Enhanced API client with retry logic and robust error handling
class APIClient {
  constructor(baseURL, options = {}) {
    this.baseURL = baseURL;
    this.defaultTimeout = options.timeout || 10000;
    this.maxRetries = options.maxRetries || 3;
    this.baseRetryDelay = options.baseRetryDelay || 1000;
  }

  async request(endpoint, options = {}) {
    const {
      method = 'GET',
      headers = {},
      body,
      timeout = this.defaultTimeout,
      retries = this.maxRetries
    } = options;

    const url = `${this.baseURL}${endpoint}`;
    const requestHeaders = {
      'Content-Type': 'application/json',
      ...headers
    };

    for (let attempt = 0; attempt <= retries; attempt++) {
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), timeout);

        const response = await fetch(url, {
          method,
          headers: requestHeaders,
          body: body ? JSON.stringify(body) : undefined,
          signal: controller.signal
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
          // Don't retry client errors (4xx)
          if (response.status >= 400 && response.status < 500) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
          }
          
          // Retry server errors (5xx) and network errors
          if (attempt === retries) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
          }
          
          // Wait before retrying with exponential backoff
          await this.sleep(this.baseRetryDelay * Math.pow(2, attempt));
          continue;
        }

        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
          return await response.json();
        }
        
        return await response.text();

      } catch (error) {
        if (error.name === 'AbortError') {
          if (attempt === retries) {
            throw new Error(`Request timeout after ${timeout}ms`);
          }
        } else if (attempt === retries) {
          throw new Error(`Network error: ${error.message}`);
        }

        // Wait before retrying with exponential backoff
        await this.sleep(this.baseRetryDelay * Math.pow(2, attempt));
      }
    }
  }

  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
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
export async function getMissions() {
  return apiClient.get('/missions');
}

export async function createMission(mission) {
  return apiClient.post('/missions', mission);
}

export async function assignAgentToMission(missionId, agentId) {
  return apiClient.post(`/missions/${missionId}/assign`, { agent_id: agentId });
}

export async function updateMissionStatus(missionId, status) {
  return apiClient.patch(`/missions/${missionId}`, { status });
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
export async function getArmadaStatus() {
  return apiClient.get('/armada/status');
}

export async function getFleetData() {
  // Fleet data is included in armada status
  const armadaData = await apiClient.get('/armada/status');
  return armadaData.fleet || [];
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

// === Utilities ===
export async function reseedDemoData() {
  return apiClient.post('/reseed');
}

// === Error Recovery ===
export async function runSelfTest() {
  return apiClient.post('/system/self-test');
}

export async function runSelfRepair() {
  return apiClient.post('/system/self-repair');
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

// Export the API client for advanced usage
export { apiClient };