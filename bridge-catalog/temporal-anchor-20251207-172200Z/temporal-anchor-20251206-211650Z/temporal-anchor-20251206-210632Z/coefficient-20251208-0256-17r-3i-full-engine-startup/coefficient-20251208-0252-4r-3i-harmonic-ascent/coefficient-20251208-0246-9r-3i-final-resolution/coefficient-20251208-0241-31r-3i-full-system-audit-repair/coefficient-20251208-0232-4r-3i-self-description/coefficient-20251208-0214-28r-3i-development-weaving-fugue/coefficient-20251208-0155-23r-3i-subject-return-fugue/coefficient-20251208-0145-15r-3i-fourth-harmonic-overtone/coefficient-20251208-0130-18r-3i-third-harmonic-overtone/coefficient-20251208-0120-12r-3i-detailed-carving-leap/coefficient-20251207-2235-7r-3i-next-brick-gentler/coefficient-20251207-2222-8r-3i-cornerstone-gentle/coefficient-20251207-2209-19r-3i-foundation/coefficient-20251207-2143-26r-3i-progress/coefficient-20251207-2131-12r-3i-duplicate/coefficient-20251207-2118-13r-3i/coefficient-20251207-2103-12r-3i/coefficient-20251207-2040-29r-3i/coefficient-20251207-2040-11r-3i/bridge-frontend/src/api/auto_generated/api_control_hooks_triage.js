// AUTO-GEN-BRIDGE v1.7.0 - CRITICAL
// Route: /api/control/hooks/triage

import apiClient from '../api';

/**
 * Auto-generated API client for /api/control/hooks/triage
 * Severity: critical
 * @param {void} 
 */
export async function api_control_hooks_triage() {
  try {
    const url = `/api/control/hooks/triage`;
    const response = await apiClient.get(url);
    return response;
  } catch (error) {
    console.error('Error calling /api/control/hooks/triage:', error);
    throw error;
  }
}
