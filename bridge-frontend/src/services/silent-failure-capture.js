/**
 * Silent Failure Capture Service
 * Monitors component health and captures failures silently
 * Part of the healing net triage systems
 */

import { DeploymentValidator } from './deployment-validator';
import { TriageEngine } from './healing-net';

/**
 * Component Health Monitor
 * Tracks health of individual components
 */
class ComponentHealthMonitor {
  constructor(componentName) {
    this.componentName = componentName;
    this.healthStatus = 'unknown';
    this.lastCheck = null;
    this.errorCount = 0;
    this.consecutiveErrors = 0;
    this.lastError = null;
  }

  /**
   * Record successful operation
   */
  recordSuccess() {
    this.healthStatus = 'healthy';
    this.lastCheck = new Date().toISOString();
    this.consecutiveErrors = 0;
  }

  /**
   * Record failure
   * @param {Error} error - Error that occurred
   */
  recordFailure(error) {
    this.healthStatus = 'unhealthy';
    this.lastCheck = new Date().toISOString();
    this.errorCount++;
    this.consecutiveErrors++;
    this.lastError = {
      message: error.message,
      timestamp: new Date().toISOString(),
      stack: error.stack
    };

    // Record in triage engine
    TriageEngine.recordDiagnostic({
      component: this.componentName,
      status: 'failure',
      error: error.message,
      timestamp: new Date().toISOString(),
      consecutiveErrors: this.consecutiveErrors
    });
  }

  /**
   * Get health status
   * @returns {Object} Health status
   */
  getStatus() {
    return {
      component: this.componentName,
      status: this.healthStatus,
      lastCheck: this.lastCheck,
      errorCount: this.errorCount,
      consecutiveErrors: this.consecutiveErrors,
      lastError: this.lastError
    };
  }

  /**
   * Reset health status
   */
  reset() {
    this.healthStatus = 'unknown';
    this.errorCount = 0;
    this.consecutiveErrors = 0;
    this.lastError = null;
  }
}

/**
 * Crash Forensics Service
 * Analyzes component crashes and provides recovery suggestions
 */
class CrashForensics {
  static crashes = [];

  /**
   * Record a component crash
   * @param {string} componentName - Name of crashed component
   * @param {Error} error - Error that caused crash
   * @param {Object} context - Additional context
   */
  static recordCrash(componentName, error, context = {}) {
    const crash = {
      component: componentName,
      error: {
        message: error.message,
        name: error.name,
        stack: error.stack
      },
      context,
      timestamp: new Date().toISOString(),
      id: `crash-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
    };

    this.crashes.push(crash);

    // Keep only last 50 crashes
    if (this.crashes.length > 50) {
      this.crashes.shift();
    }

    // Analyze crash
    const analysis = this.analyzeCrash(crash);
    
    console.error(`[CrashForensics] Component crash detected:`, {
      component: componentName,
      error: error.message,
      analysis
    });

    return analysis;
  }

  /**
   * Analyze crash and provide recovery suggestions
   * @param {Object} crash - Crash record
   * @returns {Object} Analysis and suggestions
   */
  static analyzeCrash(crash) {
    const analysis = {
      severity: 'medium',
      category: 'unknown',
      suggestions: [],
      recoverable: true
    };

    const errorMsg = crash.error.message.toLowerCase();

    // API/Network errors
    if (errorMsg.includes('fetch') || errorMsg.includes('network') || errorMsg.includes('http')) {
      analysis.category = 'network';
      analysis.suggestions.push('Check backend connectivity');
      analysis.suggestions.push('Verify API endpoints are accessible');
      analysis.suggestions.push('Enable placeholder mode until backend is available');
    }

    // JSON parsing errors
    if (errorMsg.includes('json') || errorMsg.includes('parse')) {
      analysis.category = 'data-format';
      analysis.severity = 'high';
      analysis.suggestions.push('Backend may be returning HTML instead of JSON');
      analysis.suggestions.push('Check API endpoint configuration');
      analysis.suggestions.push('Verify content-type headers');
    }

    // Missing data errors
    if (errorMsg.includes('undefined') || errorMsg.includes('null') || errorMsg.includes('cannot read')) {
      analysis.category = 'missing-data';
      analysis.suggestions.push('Add null checks before accessing data');
      analysis.suggestions.push('Use optional chaining (?.)');
      analysis.suggestions.push('Provide default values for missing data');
    }

    // Deployment-related errors
    if (errorMsg.includes('unavailable') || errorMsg.includes('offline')) {
      analysis.category = 'deployment';
      analysis.suggestions.push('Backend services not yet deployed');
      analysis.suggestions.push('Enable deployment gate for this component');
      analysis.suggestions.push('Wait for true deployment validation');
    }

    return analysis;
  }

  /**
   * Get crash history for a component
   * @param {string} componentName - Component name
   * @returns {Array} Crash history
   */
  static getCrashHistory(componentName) {
    return this.crashes.filter(c => c.component === componentName);
  }

  /**
   * Get all crashes
   * @returns {Array} All crashes
   */
  static getAllCrashes() {
    return this.crashes;
  }

  /**
   * Clear crash history
   */
  static clearHistory() {
    this.crashes = [];
  }

  /**
   * Get crash statistics
   * @returns {Object} Statistics
   */
  static getStatistics() {
    const componentStats = {};
    
    this.crashes.forEach(crash => {
      if (!componentStats[crash.component]) {
        componentStats[crash.component] = {
          count: 0,
          categories: {},
          lastCrash: null
        };
      }
      
      componentStats[crash.component].count++;
      
      const analysis = this.analyzeCrash(crash);
      componentStats[crash.component].categories[analysis.category] = 
        (componentStats[crash.component].categories[analysis.category] || 0) + 1;
      
      componentStats[crash.component].lastCrash = crash.timestamp;
    });

    return {
      totalCrashes: this.crashes.length,
      componentStats,
      recentCrashes: this.crashes.slice(-10)
    };
  }
}

/**
 * State Recovery Service
 * Helps components recover from crashes
 */
class StateRecovery {
  static savedStates = new Map();

  /**
   * Save component state
   * @param {string} componentName - Component name
   * @param {any} state - State to save
   */
  static saveState(componentName, state) {
    this.savedStates.set(componentName, {
      state,
      timestamp: Date.now()
    });
  }

  /**
   * Recover component state
   * @param {string} componentName - Component name
   * @param {number} maxAge - Maximum age in ms (default 5 minutes)
   * @returns {any} Recovered state or null
   */
  static recoverState(componentName, maxAge = 300000) {
    const saved = this.savedStates.get(componentName);
    
    if (!saved) {
      return null;
    }

    const age = Date.now() - saved.timestamp;
    
    if (age > maxAge) {
      // State too old, discard
      this.savedStates.delete(componentName);
      return null;
    }

    return saved.state;
  }

  /**
   * Clear saved state for component
   * @param {string} componentName - Component name
   */
  static clearState(componentName) {
    this.savedStates.delete(componentName);
  }

  /**
   * Clear all saved states
   */
  static clearAllStates() {
    this.savedStates.clear();
  }
}

/**
 * Silent Failure Capture - Main Service
 * Coordinates all monitoring and recovery systems
 */
class SilentFailureCapture {
  static monitors = new Map();
  static initialized = false;

  /**
   * Initialize the silent failure capture system
   */
  static async initialize() {
    if (this.initialized) {
      return;
    }

    console.log('[SilentFailureCapture] Initializing monitoring systems...');

    // Deploy component health monitors for key components
    await this.deployComponentHealthMonitors();

    // Activate crash forensics
    this.activateCrashForensics();

    // Implement state recovery
    this.implementStateRecovery();

    // Check if in true deployment
    const isDeployed = await DeploymentValidator.isTrueDeployment();
    
    if (isDeployed) {
      console.log('[SilentFailureCapture] Production monitoring enabled');
      this.enableProductionMonitoring();
    } else {
      console.log('[SilentFailureCapture] Development monitoring enabled');
    }

    this.initialized = true;
  }

  /**
   * Deploy component health monitors
   */
  static async deployComponentHealthMonitors() {
    const componentsToMonitor = [
      'agent-foundry-indoctrination',
      'mission-log',
      'admiral-keys-crypto',
      'inbox-comms',
      'vault-logs',
      'brain-console'
    ];

    componentsToMonitor.forEach(componentName => {
      const monitor = new ComponentHealthMonitor(componentName);
      this.monitors.set(componentName, monitor);
      
      // Register with triage engine for periodic checks
      TriageEngine.registerHealthMonitor(
        componentName,
        async () => {
          const status = monitor.getStatus();
          return {
            healthy: status.status === 'healthy',
            details: status
          };
        },
        120000 // Check every 2 minutes
      );
    });

    console.log(`[SilentFailureCapture] Deployed ${componentsToMonitor.length} health monitors`);
  }

  /**
   * Activate crash forensics
   */
  static activateCrashForensics() {
    // Set up global error handler
    if (typeof window !== 'undefined') {
      const originalErrorHandler = window.onerror;
      
      window.onerror = (message, source, lineno, colno, error) => {
        if (error) {
          CrashForensics.recordCrash('global', error, {
            source,
            lineno,
            colno
          });
        }
        
        // Call original handler if exists
        if (originalErrorHandler) {
          return originalErrorHandler(message, source, lineno, colno, error);
        }
        
        return false;
      };
    }

    console.log('[SilentFailureCapture] Crash forensics activated');
  }

  /**
   * Implement state recovery
   */
  static implementStateRecovery() {
    // Auto-save state periodically for monitored components
    setInterval(() => {
      // This would be implemented by components calling StateRecovery.saveState
      // Just logging here for awareness
      console.debug('[SilentFailureCapture] State recovery system active');
    }, 60000); // Every minute
  }

  /**
   * Enable production monitoring
   */
  static enableProductionMonitoring() {
    // Enhanced monitoring for production
    console.log('[SilentFailureCapture] Production monitoring active - real failures will be captured');
  }

  /**
   * Record component health check
   * @param {string} componentName - Component name
   * @param {boolean} success - Whether operation succeeded
   * @param {Error} error - Error if failed
   */
  static recordHealthCheck(componentName, success, error = null) {
    const monitor = this.monitors.get(componentName);
    
    if (!monitor) {
      // Create monitor on-the-fly
      const newMonitor = new ComponentHealthMonitor(componentName);
      this.monitors.set(componentName, newMonitor);
    }

    const activeMonitor = this.monitors.get(componentName);
    
    if (success) {
      activeMonitor.recordSuccess();
    } else {
      activeMonitor.recordFailure(error || new Error('Unknown error'));
      
      // Also record in crash forensics if error provided
      if (error) {
        CrashForensics.recordCrash(componentName, error);
      }
    }
  }

  /**
   * Get monitoring dashboard data
   * @returns {Object} Dashboard data
   */
  static getDashboardData() {
    const monitorData = Array.from(this.monitors.entries()).map(([name, monitor]) => ({
      name,
      ...monitor.getStatus()
    }));

    return {
      monitors: monitorData,
      crashes: CrashForensics.getStatistics(),
      triage: TriageEngine.getDiagnostics(),
      initialized: this.initialized
    };
  }
}

export {
  SilentFailureCapture,
  ComponentHealthMonitor,
  CrashForensics,
  StateRecovery
};

export default SilentFailureCapture;
