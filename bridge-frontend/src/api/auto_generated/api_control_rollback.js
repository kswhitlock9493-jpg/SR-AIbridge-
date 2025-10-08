// AUTO-GEN-BRIDGE v1.7.0 - CRITICAL
// Route: /api/control/rollback
// TODO: Review and integrate this auto-generated stub

import apiClient from '../api';

/**
 * Auto-generated API client for /api/control/rollback
 * Severity: critical
 * @param {void} 
 */
export async function api_control_rollback() {
  try {
    const url = `/api/control/rollback`;
    const response = await apiClient.get(url);
    return response;
  } catch (error) {
    console.error('Error calling /api/control/rollback:', error);
    throw error;
  }
}
