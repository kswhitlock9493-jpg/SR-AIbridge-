// AUTO-GEN-BRIDGE v1.7.0 - MODERATE
// Route: /engines/parser/link
// TODO: Review and integrate this auto-generated stub

import apiClient from '../api';

/**
 * Auto-generated API client for /engines/parser/link
 * Severity: moderate
 * @param {void} 
 */
export async function engines_parser_link() {
  try {
    const url = `/engines/parser/link`;
    const response = await apiClient.get(url);
    return response;
  } catch (error) {
    console.error('Error calling /engines/parser/link:', error);
    throw error;
  }
}
