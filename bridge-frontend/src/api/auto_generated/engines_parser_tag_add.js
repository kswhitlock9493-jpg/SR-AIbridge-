// AUTO-GEN-BRIDGE v1.7.0 - MODERATE
// Route: /engines/parser/tag/add

import apiClient from '../api';

/**
 * Auto-generated API client for /engines/parser/tag/add
 * Severity: moderate
 * @param {void} 
 */
export async function engines_parser_tag_add() {
  try {
    const url = `/engines/parser/tag/add`;
    const response = await apiClient.post(url);
    return response;
  } catch (error) {
    console.error('Error calling /engines/parser/tag/add:', error);
    throw error;
  }
}
