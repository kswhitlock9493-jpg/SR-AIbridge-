// AUTO-GEN-BRIDGE v1.7.0 - MODERATE
// Route: /brain/stats
// TODO: Review and integrate this auto-generated stub

import apiClient from '../api';

/**
 * Auto-generated API client for /brain/stats
 * Severity: moderate
 * @param {void} 
 */
export async function brain_stats() {
  try {
    const url = `/brain/stats`;
    const response = await apiClient.get(url);
    return response;
  } catch (error) {
    console.error('Error calling /brain/stats:', error);
    throw error;
  }
}
