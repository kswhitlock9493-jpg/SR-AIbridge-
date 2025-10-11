// AUTO-GEN-BRIDGE v1.7.0 - MODERATE
// Route: /custody/verify-drop

import apiClient from '../api';

/**
 * Auto-generated API client for /custody/verify-drop
 * Severity: moderate
 * @param {void} 
 */
export async function custody_verify_drop() {
  try {
    const url = `/custody/verify-drop`;
    const response = await apiClient.get(url);
    return response;
  } catch (error) {
    console.error('Error calling /custody/verify-drop:', error);
    throw error;
  }
}
