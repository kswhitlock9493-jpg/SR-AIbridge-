// AUTO-GEN-BRIDGE v1.7.0 - MODERATE
// Route: /engines/leviathan/solve

import apiClient from '../api';

/**
 * Auto-generated API client for /engines/leviathan/solve
 * Severity: moderate
 * @param {void} 
 */
export async function engines_leviathan_solve() {
  try {
    const url = `/engines/leviathan/solve`;
    const response = await apiClient.get(url);
    return response;
  } catch (error) {
    console.error('Error calling /engines/leviathan/solve:', error);
    throw error;
  }
}
