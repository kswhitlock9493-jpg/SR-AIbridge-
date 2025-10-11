// AUTO-GEN-BRIDGE v1.7.0 - MODERATE
// Route: /engines/truth/truths

import apiClient from '../api';

/**
 * Auto-generated API client for /engines/truth/truths
 * Severity: moderate
 * @param {void} 
 */
export async function engines_truth_truths() {
  try {
    const url = `/engines/truth/truths`;
    const response = await apiClient.get(url);
    return response;
  } catch (error) {
    console.error('Error calling /engines/truth/truths:', error);
    throw error;
  }
}
