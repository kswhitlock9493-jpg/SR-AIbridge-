// AUTO-GEN-BRIDGE v1.7.0 - MODERATE
// Route: /engines/filing/file

import apiClient from '../api';

/**
 * Auto-generated API client for /engines/filing/file
 * Severity: moderate
 * @param {void} 
 */
export async function engines_filing_file() {
  try {
    const url = `/engines/filing/file`;
    const response = await apiClient.get(url);
    return response;
  } catch (error) {
    console.error('Error calling /engines/filing/file:', error);
    throw error;
  }
}
