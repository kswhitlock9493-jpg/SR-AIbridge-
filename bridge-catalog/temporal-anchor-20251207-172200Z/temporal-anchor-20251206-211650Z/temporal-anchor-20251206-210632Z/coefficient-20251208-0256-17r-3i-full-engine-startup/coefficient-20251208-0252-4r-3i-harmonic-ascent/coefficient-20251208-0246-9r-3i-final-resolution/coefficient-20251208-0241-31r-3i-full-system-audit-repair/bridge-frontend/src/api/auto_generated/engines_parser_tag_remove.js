// AUTO-GEN-BRIDGE v1.7.0 - MODERATE
// Route: /engines/parser/tag/remove

import apiClient from '../api';

/**
 * Auto-generated API client for /engines/parser/tag/remove
 * Severity: moderate
 * @param {void} 
 */
export async function engines_parser_tag_remove() {
  try {
    const url = `/engines/parser/tag/remove`;
    const response = await apiClient.delete(url);
    return response;
  } catch (error) {
    console.error('Error calling /engines/parser/tag/remove:', error);
    throw error;
  }
}
