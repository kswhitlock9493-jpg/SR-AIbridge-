// AUTO-GEN-BRIDGE v1.7.0 - MODERATE
// Route: /engines/creativity/list

import apiClient from '../api';

/**
 * Auto-generated API client for /engines/creativity/list
 * Severity: moderate
 * @param {void} 
 */
export async function engines_creativity_list() {
  try {
    const url = `/engines/creativity/list`;
    const response = await apiClient.get(url);
    return response;
  } catch (error) {
    console.error('Error calling /engines/creativity/list:', error);
    throw error;
  }
}
