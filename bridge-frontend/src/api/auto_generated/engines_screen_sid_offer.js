// AUTO-GEN-BRIDGE v1.7.0 - MODERATE
// Route: /engines/screen/{sid}/offer
// TODO: Review and integrate this auto-generated stub

import apiClient from '../api';

/**
 * Auto-generated API client for /engines/screen/{sid}/offer
 * Severity: moderate
 * @param {sid} 
 */
export async function engines_screen_sid_offer(sid) {
  try {
    const url = `/engines/screen/${sid}/offer`;
    const response = await apiClient.get(url);
    return response;
  } catch (error) {
    console.error('Error calling /engines/screen/{sid}/offer:', error);
    throw error;
  }
}
