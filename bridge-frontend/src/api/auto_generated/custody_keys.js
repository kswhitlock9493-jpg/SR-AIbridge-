// AUTO-GEN-BRIDGE v1.7.0 - MODERATE
// Route: /custody/keys
// TODO: Review and integrate this auto-generated stub

import apiClient from '../api';

/**
 * Auto-generated API client for /custody/keys
 * Severity: moderate
 * @param {void} 
 */
export async function custody_keys() {
  try {
    const url = `/custody/keys`;
    const response = await apiClient.get(url);
    return response;
  } catch (error) {
    console.error('Error calling /custody/keys:', error);
    throw error;
  }
}
