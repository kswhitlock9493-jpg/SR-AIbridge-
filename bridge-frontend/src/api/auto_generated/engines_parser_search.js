// AUTO-GEN-BRIDGE v1.7.0 - MODERATE
// Route: /engines/parser/search
// TODO: Review and integrate this auto-generated stub

import apiClient from '../api';

/**
 * Auto-generated API client for /engines/parser/search
 * Severity: moderate
 * @param {void} 
 */
export async function engines_parser_search() {
  try {
    const url = `/engines/parser/search`;
    const response = await apiClient.get(url);
    return response;
  } catch (error) {
    console.error('Error calling /engines/parser/search:', error);
    throw error;
  }
}
