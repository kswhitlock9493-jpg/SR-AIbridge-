// AUTO-GEN-BRIDGE v1.7.0 - MODERATE
// Route: /engines/parser/list
// TODO: Review and integrate this auto-generated stub

import apiClient from '../api';

/**
 * Auto-generated API client for /engines/parser/list
 * Severity: moderate
 * @param {void} 
 */
export async function engines_parser_list() {
  try {
    const url = `/engines/parser/list`;
    const response = await apiClient.get(url);
    return response;
  } catch (error) {
    console.error('Error calling /engines/parser/list:', error);
    throw error;
  }
}
