// AUTO-GEN-BRIDGE v1.7.0 - MODERATE
// Route: /custody/admiral/rotate
// TODO: Review and integrate this auto-generated stub

import apiClient from '../api';

/**
 * Auto-generated API client for /custody/admiral/rotate
 * Severity: moderate
 * @param {void} 
 */
export async function custody_admiral_rotate() {
  try {
    const url = `/custody/admiral/rotate`;
    const response = await apiClient.put(url);
    return response;
  } catch (error) {
    console.error('Error calling /custody/admiral/rotate:', error);
    throw error;
  }
}
