// AUTO-GEN-BRIDGE v1.7.0 - MODERATE
// Route: /engines/screen/list
// TODO: Review and integrate this auto-generated stub

import apiClient from '../api';

/**
 * Auto-generated API client for /engines/screen/list
 * Severity: moderate
 * @param {void} 
 */
export async function engines_screen_list() {
  try {
    const url = `/engines/screen/list`;
    const response = await apiClient.get(url);
    return response;
  } catch (error) {
    console.error('Error calling /engines/screen/list:', error);
    throw error;
  }
}
