// AUTO-GEN-BRIDGE v1.7.0 - MODERATE
// Route: /fleet
// TODO: Review and integrate this auto-generated stub

import apiClient from '../api';

/**
 * Auto-generated API client for /fleet
 * Severity: moderate
 * @param {void} 
 */
export async function fleet() {
  try {
    const url = `/fleet`;
    const response = await apiClient.get(url);
    return response;
  } catch (error) {
    console.error('Error calling /fleet:', error);
    throw error;
  }
}
