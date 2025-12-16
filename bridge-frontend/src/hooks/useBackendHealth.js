// Bootstrap module for BRH backend health checks
// This ensures the backend is live before enabling production features

import { ensureLiveBackend } from '../api/brh';

let backendHealthy = null;
let lastCheck = 0;
const CACHE_DURATION = 30000; // Cache health check for 30 seconds

/**
 * Check if BRH backend is live and responsive
 * Results are cached to avoid excessive health checks
 * @returns {Promise<boolean>} True if backend is healthy
 */
export async function checkBackendHealth() {
  const now = Date.now();
  
  // Return cached result if still valid
  if (backendHealthy !== null && (now - lastCheck) < CACHE_DURATION) {
    return backendHealthy;
  }
  
  // Perform health check
  try {
    backendHealthy = await ensureLiveBackend();
    lastCheck = now;
    return backendHealthy;
  } catch (error) {
    console.error('[Bootstrap] Backend health check failed:', error);
    backendHealthy = false;
    lastCheck = now;
    return false;
  }
}

/**
 * Initialize the application by checking backend health
 * Call this during app startup
 * @returns {Promise<{healthy: boolean, mode: string}>}
 */
export async function initializeApp() {
  const healthy = await checkBackendHealth();
  
  return {
    healthy,
    mode: healthy ? 'production' : 'offline',
    message: healthy 
      ? 'BRH backend is live' 
      : 'BRH backend is offline - limited functionality'
  };
}

/**
 * Force a fresh health check (bypass cache)
 * @returns {Promise<boolean>}
 */
export async function refreshBackendHealth() {
  backendHealthy = null;
  lastCheck = 0;
  return checkBackendHealth();
}
