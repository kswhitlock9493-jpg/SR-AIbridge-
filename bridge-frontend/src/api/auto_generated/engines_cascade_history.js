// AUTO-GEN-BRIDGE v1.7.0 - MODERATE
// Route: /engines/cascade/history

import apiClient from '../api';

/**
 * Auto-generated API client for /engines/cascade/history
 * Severity: moderate
 * @param {void} 
 */
export async function engines_cascade_history() {
  try {
    const url = `/engines/cascade/history`;
    const response = await apiClient.get(url);
    return response;
  } catch (error) {
    console.error('Error calling /engines/cascade/history:', error);
    throw error;
  }
}
