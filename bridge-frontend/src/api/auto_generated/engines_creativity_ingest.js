// AUTO-GEN-BRIDGE v1.7.0 - MODERATE
// Route: /engines/creativity/ingest

import apiClient from '../api';

/**
 * Auto-generated API client for /engines/creativity/ingest
 * Severity: moderate
 * @param {void} 
 */
export async function engines_creativity_ingest() {
  try {
    const url = `/engines/creativity/ingest`;
    const response = await apiClient.post(url);
    return response;
  } catch (error) {
    console.error('Error calling /engines/creativity/ingest:', error);
    throw error;
  }
}
