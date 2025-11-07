/**
 * True Data Revealer Service
 * Manages transition between placeholder and real data
 * Only switches to real data when deployment validation passes
 */

import { DeploymentValidator } from './deployment-validator';
import { BRHService } from './brh-api';
import { UmbraLattice } from './healing-net';
import config from '../config';

/**
 * TrueDataRevealer - Manages data mode transitions
 */
class TrueDataRevealer {
  constructor() {
    this.placeholderMode = true;
    this.trueDataMode = false;
    this.dataCache = new Map();
  }

  /**
   * Transition to real data mode
   * Only when paranoid deployment conditions are met
   * @returns {Promise<string>} Transition status
   */
  async transitionToRealData() {
    try {
      const validation = await DeploymentValidator.validateTrueDeployment();
      
      if (validation.trueDeployment) {
        this.placeholderMode = false;
        this.trueDataMode = true;
        console.log('[TrueDataRevealer] ✅ REAL_DATA_ACTIVATED');
        return 'REAL_DATA_ACTIVATED';
      }
      
      console.log('[TrueDataRevealer] 🔒 PLACEHOLDER_MODE_ACTIVE');
      return 'PLACEHOLDER_MODE_ACTIVE';
    } catch (error) {
      console.error('[TrueDataRevealer] Validation failed:', error);
      return 'VALIDATION_FAILED';
    }
  }

  /**
   * Check if in true data mode
   * @returns {boolean} True if real data should be used
   */
  isTrueDataMode() {
    return this.trueDataMode;
  }

  /**
   * Get data with automatic mode detection
   * Returns real data if in true mode, placeholder otherwise
   * @param {string} endpoint - API endpoint
   * @param {Function} realDataFetcher - Function to fetch real data
   * @param {any} placeholderData - Placeholder data to use
   * @returns {Promise<any>} Data (real or placeholder)
   */
  async getData(endpoint, realDataFetcher, placeholderData) {
    // Check deployment status first
    const isDeployed = await DeploymentValidator.isTrueDeployment();
    
    if (isDeployed) {
      try {
        // Attempt to get real data
        const realData = await realDataFetcher();
        
        // Cache successful real data
        this.dataCache.set(endpoint, {
          data: realData,
          timestamp: Date.now(),
          type: 'real'
        });
        
        return realData;
      } catch (error) {
        console.warn(`[TrueDataRevealer] Real data fetch failed for ${endpoint}, using placeholder:`, error.message);
        return placeholderData;
      }
    }
    
    // Not deployed or fetch failed - return placeholder
    return placeholderData;
  }

  /**
   * Clear data cache
   */
  clearCache() {
    this.dataCache.clear();
  }

  /**
   * Get cache statistics
   * @returns {Object} Cache stats
   */
  getCacheStats() {
    return {
      size: this.dataCache.size,
      entries: Array.from(this.dataCache.entries()).map(([key, value]) => ({
        endpoint: key,
        type: value.type,
        age: Date.now() - value.timestamp
      }))
    };
  }
}

/**
 * Real Mission Service
 * Manages mission data with deployment awareness
 */
class RealMissionService {
  static dataRevealer = new TrueDataRevealer();

  /**
   * Get missions with deployment-aware data
   * @param {Object} filters - Optional filters
   * @returns {Promise<Array>} Mission data (real or placeholder)
   */
  static async getMissions(filters = {}) {
    const placeholderMissions = [
      {
        id: 'placeholder-1',
        title: 'System Initialization',
        description: 'Backend systems are initializing. Real missions will appear when deployment is complete.',
        status: 'pending',
        priority: 'medium',
        captain: 'System',
        progress: 0,
        isPlaceholder: true
      }
    ];

    return await this.dataRevealer.getData(
      '/missions',
      () => BRHService.getMissions(filters),
      placeholderMissions
    );
  }

  /**
   * Check if currently showing real missions
   * @returns {Promise<boolean>} True if real data mode
   */
  static async isShowingRealData() {
    return await DeploymentValidator.isTrueDeployment();
  }
}

/**
 * Real Agent Service
 * Manages agent data with deployment awareness
 */
class RealAgentService {
  static dataRevealer = new TrueDataRevealer();

  /**
   * Get agents with deployment-aware data
   * @returns {Promise<Array>} Agent data (real or placeholder)
   */
  static async getAgents() {
    const placeholderAgents = [
      {
        id: 'placeholder-agent-1',
        name: 'Placeholder Agent',
        role: 'System',
        status: 'initializing',
        specialties: ['System initialization'],
        certified: false,
        isPlaceholder: true
      }
    ];

    return await this.dataRevealer.getData(
      '/engines/indoctrination/agents',
      () => BRHService.getAgents(),
      placeholderAgents
    );
  }
}

/**
 * Real Vault Service
 * Manages vault logs with deployment awareness
 */
class RealVaultService {
  static dataRevealer = new TrueDataRevealer();

  /**
   * Get vault logs with deployment-aware data
   * @param {Object} filters - Optional filters
   * @returns {Promise<Array>} Vault log data (real or placeholder)
   */
  static async getVaultLogs(filters = {}) {
    const placeholderLogs = [
      {
        id: 'placeholder-log-1',
        timestamp: new Date().toISOString(),
        level: 'info',
        message: 'Vault system initializing. Real logs will appear when deployment is complete.',
        source: 'System',
        isPlaceholder: true
      }
    ];

    return await this.dataRevealer.getData(
      '/vault/logs',
      () => BRHService.getVaultLogs(filters),
      placeholderLogs
    );
  }
}

/**
 * Real Admiral Keys Service
 * Manages custody/keys data with deployment awareness
 */
class RealAdmiralKeysService {
  static dataRevealer = new TrueDataRevealer();

  /**
   * Get custody status with deployment-aware data
   * @returns {Promise<Object>} Custody status (real or placeholder)
   */
  static async getCustodyStatus() {
    const placeholderStatus = {
      status: 'initializing',
      message: 'Custody system initializing. Real keys will be available when deployment is complete.',
      keys: [],
      isPlaceholder: true
    };

    return await this.dataRevealer.getData(
      '/custody/status',
      async () => {
        const response = await fetch(`${config.API_BASE_URL}/custody/status`);
        if (!response.ok) throw new Error('Fetch failed');
        return await response.json();
      },
      placeholderStatus
    );
  }
}

/**
 * Inbox Stabilization Service
 * Prevents inbox crashes by checking deployment before loading
 */
class StableInboxService {
  /**
   * Initialize inbox only when systems are ready
   * @returns {Promise<Object>} Inbox initialization status
   */
  static async initialize() {
    const isDeployed = await DeploymentValidator.isTrueDeployment();
    
    if (!isDeployed) {
      return {
        initialized: false,
        mode: 'placeholder',
        message: 'Inbox will be available when communication systems are deployed'
      };
    }

    try {
      // Check if comms system is operational
      const validation = await DeploymentValidator.validateTrueDeployment();
      
      if (validation.validationDetails.brh_integration) {
        return {
          initialized: true,
          mode: 'operational',
          message: 'Inbox operational'
        };
      }
    } catch (error) {
      console.error('[StableInbox] Initialization failed:', error);
    }

    return {
      initialized: false,
      mode: 'degraded',
      message: 'Communication systems not yet ready'
    };
  }

  /**
   * Get messages with stability checks
   * @returns {Promise<Array>} Messages (real or placeholder)
   */
  static async getMessages() {
    const initStatus = await this.initialize();
    
    if (!initStatus.initialized) {
      return [{
        id: 'placeholder-msg-1',
        from: 'System',
        subject: 'Inbox Initializing',
        message: initStatus.message,
        timestamp: new Date().toISOString(),
        isPlaceholder: true
      }];
    }

    try {
      // Fetch real messages
      const response = await fetch(`${config.API_BASE_URL}/captains/messages`);
      if (!response.ok) throw new Error('Fetch failed');
      const data = await response.json();
      return Array.isArray(data) ? data : (data.messages || []);
    } catch (error) {
      console.error('[StableInbox] Message fetch failed:', error);
      return UmbraLattice.getFallbackData('/captains/messages').messages || [];
    }
  }
}

export {
  TrueDataRevealer,
  RealMissionService,
  RealAgentService,
  RealVaultService,
  RealAdmiralKeysService,
  StableInboxService
};

export default TrueDataRevealer;
