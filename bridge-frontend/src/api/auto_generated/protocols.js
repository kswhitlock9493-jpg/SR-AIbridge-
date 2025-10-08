// AUTO-GEN-BRIDGE v1.7.0 - MODERATE
// Route: /protocols/
// TODO: Review and integrate this auto-generated stub

import apiClient from '../api';

/**
 * Auto-generated API client for /protocols/
 * Severity: moderate
 * @param {void} 
 */
export async function protocols() {
  try {
    const url = `/protocols/`;
    const response = await apiClient.get(url);
    return response;
  } catch (error) {
    console.error('Error calling /protocols/:', error);
    throw error;
  }
}
