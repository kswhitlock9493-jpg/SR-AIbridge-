// AUTO-GEN-BRIDGE v1.7.0 - MODERATE
// Route: /brain/export

import apiClient from '../api';

/**
 * Auto-generated API client for /brain/export
 * Severity: moderate
 * @param {void} 
 */
export async function brain_export() {
  try {
    const url = `/brain/export`;
    const response = await apiClient.get(url);
    return response;
  } catch (error) {
    console.error('Error calling /brain/export:', error);
    throw error;
  }
}
