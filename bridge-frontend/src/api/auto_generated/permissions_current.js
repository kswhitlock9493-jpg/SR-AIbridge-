// AUTO-GEN-BRIDGE v1.7.0 - MODERATE
// Route: /permissions/current
// TODO: Review and integrate this auto-generated stub

import apiClient from '../api';

/**
 * Auto-generated API client for /permissions/current
 * Severity: moderate
 * @param {void} 
 */
export async function permissions_current() {
  try {
    const url = `/permissions/current`;
    const response = await apiClient.get(url);
    return response;
  } catch (error) {
    console.error('Error calling /permissions/current:', error);
    throw error;
  }
}
