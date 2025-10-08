// AUTO-GEN-BRIDGE v1.7.0 - MODERATE
// Route: /engines/filing/search
// TODO: Review and integrate this auto-generated stub

import apiClient from '../api';

/**
 * Auto-generated API client for /engines/filing/search
 * Severity: moderate
 * @param {void} 
 */
export async function engines_filing_search() {
  try {
    const url = `/engines/filing/search`;
    const response = await apiClient.get(url);
    return response;
  } catch (error) {
    console.error('Error calling /engines/filing/search:', error);
    throw error;
  }
}
