// AUTO-GEN-BRIDGE v1.7.0 - MODERATE
// Route: /console/summary
// TODO: Review and integrate this auto-generated stub

import apiClient from '../api';

/**
 * Auto-generated API client for /console/summary
 * Severity: moderate
 * @param {void} 
 */
export async function console_summary() {
  try {
    const url = `/console/summary`;
    const response = await apiClient.get(url);
    return response;
  } catch (error) {
    console.error('Error calling /console/summary:', error);
    throw error;
  }
}
