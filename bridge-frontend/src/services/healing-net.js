/**
 * Healing Net Service - Umbra Lattice Integration
 * Provides graceful degradation, fallback mechanisms, and error recovery
 * for API failures and component crashes
 */

import { buildURL } from '../utils/endpoint-transformer';

class HealingNetException extends Error {
  constructor(message, context = {}) {
    super(message);
    this.name = 'HealingNetException';
    this.context = context;
    this.timestamp = new Date().toISOString();
  }
}

class UmbraLattice {
  static fallbackData = {
    '/missions': {
      missions: [],
      status: 'offline',
      message: 'Mission system temporarily unavailable'
    },
    '/brain/stats': {
      total_memories: 0,
      categories: [],
      tier: 'captain',
      memory_autonomy: { retention: '14hr', max_memories: 10000 }
    },
    '/brain/memories': [],
    '/custody/status': {
      status: 'offline',
      message: 'Custody system temporarily unavailable'
    },
    '/custody/keys': {
      keys: [],
      message: 'Key management temporarily unavailable'
    },
    '/engines/indoctrination/agents': [],
    '/armada/status': {
      fleet: [],
      status: 'offline'
    },
    '/vault/logs': {
      logs: [],
      message: 'Vault logs temporarily unavailable'
    },
    '/status': {
      status: 'degraded',
      message: 'System operating in degraded mode'
    }
  };

  static getFallbackData(endpoint) {
    // Extract base endpoint without query params
    const baseEndpoint = endpoint.split('?')[0];
    
    // Check for exact match
    if (this.fallbackData[baseEndpoint]) {
      return this.fallbackData[baseEndpoint];
    }

    // Check for partial matches
    for (const [key, value] of Object.entries(this.fallbackData)) {
      if (baseEndpoint.startsWith(key)) {
        return value;
      }
    }

    // Default fallback
    return {
      status: 'unavailable',
      message: 'Service temporarily unavailable',
      data: null
    };
  }

  static recordFailure(endpoint, error) {
    const failures = this.getFailureLog();
    failures.push({
      endpoint,
      error: error.message,
      timestamp: new Date().toISOString(),
      context: error.context || {}
    });

    // Keep only last 100 failures
    if (failures.length > 100) {
      failures.shift();
    }

    try {
      localStorage.setItem('healing_net_failures', JSON.stringify(failures));
    } catch (e) {
      // Ignore storage errors
      console.warn('Failed to persist failure log:', e);
    }
  }

  static getFailureLog() {
    try {
      const log = localStorage.getItem('healing_net_failures');
      return log ? JSON.parse(log) : [];
    } catch (e) {
      return [];
    }
  }

  static clearFailureLog() {
    try {
      localStorage.removeItem('healing_net_failures');
    } catch (e) {
      // Ignore
    }
  }
}

class APIGuardian {
  static async safeFetch(endpoint, options = {}) {
    const {
      method = 'GET',
      headers = {},
      body,
      timeout = 10000,
      retries = 2,
      fallbackOnError = true,
      baseURL
    } = options;

    // Build the full URL using the transformer utility
    const url = typeof endpoint === 'string' && endpoint.startsWith('http') 
      ? endpoint 
      : buildURL(endpoint, baseURL);

    for (let attempt = 0; attempt <= retries; attempt++) {
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), timeout);

        const response = await fetch(url, {
          method,
          headers: {
            'Content-Type': 'application/json',
            ...headers
          },
          body: body ? JSON.stringify(body) : undefined,
          signal: controller.signal
        });

        clearTimeout(timeoutId);

        // Check content type - HEALING NET INTERVENTION
        const contentType = response.headers.get('content-type');
        if (!contentType?.includes('application/json')) {
          throw new HealingNetException(
            'HTML response detected - expected JSON',
            { endpoint, contentType, status: response.status }
          );
        }

        if (!response.ok) {
          if (response.status >= 400 && response.status < 500) {
            // Client error - don't retry
            throw new HealingNetException(
              `HTTP ${response.status}: ${response.statusText}`,
              { endpoint, status: response.status }
            );
          }

          // Server error - retry
          if (attempt < retries) {
            await this.sleep(Math.pow(2, attempt) * 1000);
            continue;
          }

          throw new HealingNetException(
            `HTTP ${response.status}: ${response.statusText}`,
            { endpoint, status: response.status }
          );
        }

        return await response.json();

      } catch (error) {
        const isLastAttempt = attempt === retries;
        
        if (error.name === 'AbortError') {
          if (!isLastAttempt) {
            await this.sleep(Math.pow(2, attempt) * 1000);
            continue;
          }
          throw new HealingNetException(
            `Request timeout after ${timeout}ms`,
            { endpoint, timeout }
          );
        }

        if (!isLastAttempt && !(error instanceof HealingNetException && error.context.status < 500)) {
          await this.sleep(Math.pow(2, attempt) * 1000);
          continue;
        }

        // Last attempt failed - use fallback if enabled
        if (fallbackOnError) {
          console.warn(`[HealingNet] API failure for ${endpoint}, using fallback data:`, error.message);
          UmbraLattice.recordFailure(endpoint, error);
          return UmbraLattice.getFallbackData(endpoint);
        }

        throw error;
      }
    }
  }

  static sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  static async guardedApiCall(endpoint, options = {}) {
    return this.safeFetch(endpoint, { ...options, fallbackOnError: true });
  }
}

class CircuitBreaker {
  constructor(name, options = {}) {
    this.name = name;
    this.failureThreshold = options.failureThreshold || 5;
    this.resetTimeout = options.resetTimeout || 60000; // 1 minute
    this.failureCount = 0;
    this.state = 'CLOSED'; // CLOSED, OPEN, HALF_OPEN
    this.nextAttempt = null;
  }

  async execute(fn) {
    if (this.state === 'OPEN') {
      if (Date.now() < this.nextAttempt) {
        throw new HealingNetException(
          `Circuit breaker ${this.name} is OPEN`,
          { state: this.state, nextAttempt: this.nextAttempt }
        );
      }
      this.state = 'HALF_OPEN';
    }

    try {
      const result = await fn();
      this.onSuccess();
      return result;
    } catch (error) {
      this.onFailure();
      throw error;
    }
  }

  onSuccess() {
    this.failureCount = 0;
    this.state = 'CLOSED';
    this.nextAttempt = null;
  }

  onFailure() {
    this.failureCount++;
    if (this.failureCount >= this.failureThreshold) {
      this.state = 'OPEN';
      this.nextAttempt = Date.now() + this.resetTimeout;
      console.warn(`[CircuitBreaker] ${this.name} is now OPEN until ${new Date(this.nextAttempt).toISOString()}`);
    }
  }

  reset() {
    this.failureCount = 0;
    this.state = 'CLOSED';
    this.nextAttempt = null;
  }

  getState() {
    return {
      name: this.name,
      state: this.state,
      failureCount: this.failureCount,
      nextAttempt: this.nextAttempt
    };
  }
}

class TriageEngine {
  static diagnostics = [];
  static healthMonitors = new Map();

  static registerHealthMonitor(name, checkFn, interval = 60000) {
    const monitor = {
      name,
      checkFn,
      interval,
      lastCheck: null,
      lastStatus: null,
      intervalId: null
    };

    monitor.intervalId = setInterval(async () => {
      try {
        const status = await checkFn();
        monitor.lastCheck = new Date().toISOString();
        monitor.lastStatus = status;
        
        if (!status.healthy) {
          this.recordDiagnostic({
            component: name,
            status: 'unhealthy',
            details: status,
            timestamp: new Date().toISOString()
          });
        }
      } catch (error) {
        monitor.lastStatus = { healthy: false, error: error.message };
        this.recordDiagnostic({
          component: name,
          status: 'check_failed',
          error: error.message,
          timestamp: new Date().toISOString()
        });
      }
    }, interval);

    this.healthMonitors.set(name, monitor);
    return monitor;
  }

  static unregisterHealthMonitor(name) {
    const monitor = this.healthMonitors.get(name);
    if (monitor && monitor.intervalId) {
      clearInterval(monitor.intervalId);
      this.healthMonitors.delete(name);
    }
  }

  static recordDiagnostic(diagnostic) {
    this.diagnostics.push(diagnostic);
    if (this.diagnostics.length > 1000) {
      this.diagnostics.shift();
    }
  }

  static getDiagnostics() {
    return {
      diagnostics: this.diagnostics,
      monitors: Array.from(this.healthMonitors.values()).map(m => ({
        name: m.name,
        lastCheck: m.lastCheck,
        lastStatus: m.lastStatus
      })),
      failureLog: UmbraLattice.getFailureLog()
    };
  }

  static clearDiagnostics() {
    this.diagnostics = [];
    UmbraLattice.clearFailureLog();
  }
}

export {
  APIGuardian,
  UmbraLattice,
  HealingNetException,
  CircuitBreaker,
  TriageEngine
};
