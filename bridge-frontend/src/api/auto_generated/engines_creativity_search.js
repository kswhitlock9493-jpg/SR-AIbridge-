// AUTO-GEN-BRIDGE v1.7.0 - MODERATE
// Route: /engines/creativity/search
// TODO: Review and integrate this auto-generated stub

import apiClient from '../api';

/**
 * Auto-generated API client for /engines/creativity/search
 * Severity: moderate
 * @param {void} 
 */
export async function engines_creativity_search() {
  try {
    const url = `/engines/creativity/search`;
    const response = await apiClient.get(url);
    return response;
  } catch (error) {
    console.error('Error calling /engines/creativity/search:', error);
    throw error;
  }
}
