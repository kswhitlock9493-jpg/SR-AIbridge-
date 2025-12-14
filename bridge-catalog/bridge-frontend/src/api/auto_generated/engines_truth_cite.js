// AUTO-GEN-BRIDGE v1.7.0 - MODERATE
// Route: /engines/truth/cite

import apiClient from '../api';

/**
 * Auto-generated API client for /engines/truth/cite
 * Severity: moderate
 * @param {void} 
 */
export async function engines_truth_cite() {
  try {
    const url = `/engines/truth/cite`;
    const response = await apiClient.get(url);
    return response;
  } catch (error) {
    console.error('Error calling /engines/truth/cite:', error);
    throw error;
  }
}
