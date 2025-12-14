// AUTO-GEN-BRIDGE v1.7.0 - MODERATE
// Route: /engines/screen/{sid}/ice

import apiClient from '../api';

/**
 * Auto-generated API client for /engines/screen/{sid}/ice
 * Severity: moderate
 * @param {sid} 
 */
export async function engines_screen_sid_ice(sid) {
  try {
    const url = `/engines/screen/${sid}/ice`;
    const response = await apiClient.get(url);
    return response;
  } catch (error) {
    console.error('Error calling /engines/screen/{sid}/ice:', error);
    throw error;
  }
}
