/**
 * Deployment Validator - True Deployment Detection
 * Validates all systems are properly deployed before revealing true functionality
 * Part of the paranoid security unlock sequence
 */

import config from '../config';
import { APIGuardian } from './healing-net';

const API_BASE = config.API_BASE_URL;

/**
 * Validation status for individual systems
 */
class SystemValidator {
  /**
   * Validate BRH (Bridge Runtime Handler) integration
   * @returns {Promise<boolean>} True if BRH is responding correctly
   */
  static async validateBRH() {
    try {
      const response = await APIGuardian.safeFetch(`${API_BASE}/status`, {
        timeout: 5000,
        retries: 1,
        fallbackOnError: false
      });
      
      // Check for valid BRH response structure
      return response && 
             typeof response === 'object' && 
             !response.error &&
             response.status !== 'offline' &&
             response.status !== 'unavailable';
    } catch (error) {
      console.warn('[DeploymentValidator] BRH validation failed:', error.message);
      return false;
    }
  }

  /**
   * Validate Healing Net is operational
   * @returns {Promise<boolean>} True if healing net is active
   */
  static async validateHealingNet() {
    try {
      const response = await APIGuardian.safeFetch(`${API_BASE}/health`, {
        timeout: 5000,
        retries: 1,
        fallbackOnError: false
      });
      
      return response && 
             response.status !== 'unhealthy' &&
             response.status !== 'offline';
    } catch (error) {
      console.warn('[DeploymentValidator] Healing Net validation failed:', error.message);
      return false;
    }
  }

  /**
   * Validate Crypto/Admiral Keys system
   * @returns {Promise<boolean>} True if crypto system is initialized
   */
  static async validateCrypto() {
    try {
      // Check if custody endpoint is accessible
      const response = await APIGuardian.safeFetch(`${API_BASE}/custody/status`, {
        timeout: 5000,
        retries: 1,
        fallbackOnError: false
      });
      
      return response && 
             response.status !== 'offline' &&
             response.status !== 'unavailable';
    } catch (error) {
      console.warn('[DeploymentValidator] Crypto validation failed:', error.message);
      return false;
    }
  }

  /**
   * Validate Umbra Lattice (shadow operations)
   * @returns {Promise<boolean>} True if umbra lattice is active
   */
  static async validateUmbra() {
    try {
      // Umbra lattice is part of the healing net system
      // Check if fallback mechanisms are working
      const response = await APIGuardian.safeFetch(`${API_BASE}/health/full`, {
        timeout: 5000,
        retries: 1,
        fallbackOnError: false
      });
      
      return response && 
             response.components && 
             Object.keys(response.components).length > 0;
    } catch (error) {
      console.warn('[DeploymentValidator] Umbra validation failed:', error.message);
      return false;
    }
  }

  /**
   * Validate Indoctrination Engine
   * @returns {Promise<boolean>} True if indoctrination engine is operational
   */
  static async validateIndoctrination() {
    try {
      const response = await APIGuardian.safeFetch(`${API_BASE}/engines/indoctrination/status`, {
        timeout: 5000,
        retries: 1,
        fallbackOnError: false
      });
      
      return response && 
             response.status !== 'offline' &&
             response.status !== 'unavailable';
    } catch (error) {
      console.warn('[DeploymentValidator] Indoctrination validation failed:', error.message);
      return false;
    }
  }
}

/**
 * Main Deployment Validator
 * Coordinates all system validation checks
 */
class DeploymentValidator {
  static validationCache = null;
  static lastValidation = null;
  static CACHE_TTL = 60000; // 1 minute cache

  /**
   * Validate true deployment status
   * Checks all required systems are operational
   * @param {boolean} useCache - Whether to use cached results
   * @returns {Promise<Object>} Deployment validation results
   */
  static async validateTrueDeployment(useCache = true) {
    // Check cache
    if (useCache && this.validationCache && this.lastValidation) {
      const cacheAge = Date.now() - this.lastValidation;
      if (cacheAge < this.CACHE_TTL) {
        return this.validationCache;
      }
    }

    console.log('[DeploymentValidator] Starting true deployment validation...');
    
    // Run all validation checks in parallel
    const [brh, healingNet, crypto, umbra, indoctrination] = await Promise.all([
      SystemValidator.validateBRH(),
      SystemValidator.validateHealingNet(),
      SystemValidator.validateCrypto(),
      SystemValidator.validateUmbra(),
      SystemValidator.validateIndoctrination()
    ]);

    const validationChecks = {
      brh_integration: brh,
      healing_net: healingNet,
      crypto_handshake: crypto,
      umbra_lattice: umbra,
      indoctrination: indoctrination
    };

    // True deployment requires ALL checks to pass
    const trueDeployment = Object.values(validationChecks).every(v => v === true);

    const result = {
      trueDeployment,
      validationDetails: validationChecks,
      timestamp: new Date().toISOString(),
      systemsOnline: Object.values(validationChecks).filter(v => v).length,
      totalSystems: Object.keys(validationChecks).length
    };

    // Cache results
    this.validationCache = result;
    this.lastValidation = Date.now();

    console.log('[DeploymentValidator] Validation complete:', result);
    
    if (trueDeployment) {
      console.log('🎉 TRUE BRIDGE REVEALED: All paranoid conditions met!');
    } else {
      console.log('🕵️ Bridge in placeholder mode: True deployment not yet achieved');
      console.log('Failed systems:', Object.entries(validationChecks)
        .filter(([_, v]) => !v)
        .map(([k]) => k)
        .join(', '));
    }

    return result;
  }

  /**
   * Check if system is in true deployment mode
   * @returns {Promise<boolean>} True if all systems are validated
   */
  static async isTrueDeployment() {
    const result = await this.validateTrueDeployment();
    return result.trueDeployment;
  }

  /**
   * Clear validation cache to force re-check
   */
  static clearCache() {
    this.validationCache = null;
    this.lastValidation = null;
  }

  /**
   * Get current deployment mode (cached)
   * @returns {string} 'production' | 'development' | 'degraded'
   */
  static getDeploymentMode() {
    if (!this.validationCache) {
      return 'unknown';
    }

    if (this.validationCache.trueDeployment) {
      return 'production';
    }

    const systemsOnline = this.validationCache.systemsOnline;
    const totalSystems = this.validationCache.totalSystems;
    
    if (systemsOnline === 0) {
      return 'development';
    }

    if (systemsOnline < totalSystems) {
      return 'degraded';
    }

    return 'development';
  }

  /**
   * Get detailed validation status for UI display
   * @returns {Object} Validation status with details
   */
  static getValidationStatus() {
    if (!this.validationCache) {
      return {
        mode: 'unknown',
        message: 'Validation not yet performed',
        details: {}
      };
    }

    const mode = this.getDeploymentMode();
    const { validationDetails, systemsOnline, totalSystems } = this.validationCache;

    const messages = {
      production: '🎉 All systems operational - True Bridge revealed',
      degraded: `⚠️ Partial deployment - ${systemsOnline}/${totalSystems} systems online`,
      development: '🛠️ Development mode - Using placeholders',
      unknown: '❓ Validation status unknown'
    };

    return {
      mode,
      message: messages[mode] || messages.unknown,
      details: validationDetails,
      systemsOnline,
      totalSystems,
      timestamp: this.validationCache.timestamp
    };
  }
}

/**
 * Component Unlock Controller
 * Manages component visibility based on deployment validation
 */
class ComponentUnlockController {
  static unlockedComponents = new Set();

  /**
   * Unlock components when true deployment is achieved
   * @returns {Promise<string>} Unlock status
   */
  static async unlockComponents() {
    const deploymentStatus = await DeploymentValidator.validateTrueDeployment();

    if (deploymentStatus.trueDeployment) {
      // Unlock all true functionality
      this.unlockComponent('AgentFoundry');
      this.unlockComponent('MissionLog');
      this.unlockComponent('Inbox');
      this.unlockComponent('AdmiralKeys');
      this.unlockComponent('BrainConsole');
      
      console.log('🎉 TRUE BRIDGE REVEALED: All paranoid conditions met!');
      return 'FULL_OPERATIONAL_STATUS_ACHIEVED';
    } else {
      console.log('🕵️ Bridge remains in placeholder mode: True deployment not yet achieved');
      return 'PLACEHOLDER_MODE_ACTIVE';
    }
  }

  /**
   * Unlock specific component
   * @param {string} componentName - Name of component to unlock
   */
  static unlockComponent(componentName) {
    this.unlockedComponents.add(componentName);
  }

  /**
   * Check if component is unlocked
   * @param {string} componentName - Name of component to check
   * @returns {boolean} True if component is unlocked
   */
  static isComponentUnlocked(componentName) {
    return this.unlockedComponents.has(componentName);
  }

  /**
   * Lock all components (for testing or mode switch)
   */
  static lockAllComponents() {
    this.unlockedComponents.clear();
  }
}

export {
  DeploymentValidator,
  SystemValidator,
  ComponentUnlockController
};

export default DeploymentValidator;
