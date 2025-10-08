// AUTO-GEN-BRIDGE v1.7.0 - MODERATE
// Route: /scans/
// TODO: Review and integrate this auto-generated stub

import apiClient from '../api';

/**
 * Auto-generated API client for /scans/
 * Severity: moderate
 * @param {void} 
 */
export async function scans() {
  try {
    const url = `/scans/`;
    const response = await apiClient.get(url);
    return response;
  } catch (error) {
    console.error('Error calling /scans/:', error);
    throw error;
  }
}
