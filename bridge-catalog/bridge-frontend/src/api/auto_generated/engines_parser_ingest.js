// AUTO-GEN-BRIDGE v1.7.0 - MODERATE
// Route: /engines/parser/ingest

import apiClient from '../api';

/**
 * Auto-generated API client for /engines/parser/ingest
 * Severity: moderate
 * @param {void} 
 */
export async function engines_parser_ingest() {
  try {
    const url = `/engines/parser/ingest`;
    const response = await apiClient.post(url);
    return response;
  } catch (error) {
    console.error('Error calling /engines/parser/ingest:', error);
    throw error;
  }
}
