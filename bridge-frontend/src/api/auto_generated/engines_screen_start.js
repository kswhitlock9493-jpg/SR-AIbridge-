// AUTO-GEN-BRIDGE v1.7.0 - MODERATE
// Route: /engines/screen/start

import apiClient from '../api';

/**
 * Auto-generated API client for /engines/screen/start
 * Severity: moderate
 * @param {void} 
 */
export async function engines_screen_start() {
  try {
    const url = `/engines/screen/start`;
    const response = await apiClient.get(url);
    return response;
  } catch (error) {
    console.error('Error calling /engines/screen/start:', error);
    throw error;
  }
}
