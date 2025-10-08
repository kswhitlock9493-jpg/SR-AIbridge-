// AUTO-GEN-BRIDGE v1.7.0 - MODERATE
// Route: /brain/
// TODO: Review and integrate this auto-generated stub

import apiClient from '../api';

/**
 * Auto-generated API client for /brain/
 * Severity: moderate
 * @param {void} 
 */
export async function brain() {
  try {
    const url = `/brain/`;
    const response = await apiClient.get(url);
    return response;
  } catch (error) {
    console.error('Error calling /brain/:', error);
    throw error;
  }
}
