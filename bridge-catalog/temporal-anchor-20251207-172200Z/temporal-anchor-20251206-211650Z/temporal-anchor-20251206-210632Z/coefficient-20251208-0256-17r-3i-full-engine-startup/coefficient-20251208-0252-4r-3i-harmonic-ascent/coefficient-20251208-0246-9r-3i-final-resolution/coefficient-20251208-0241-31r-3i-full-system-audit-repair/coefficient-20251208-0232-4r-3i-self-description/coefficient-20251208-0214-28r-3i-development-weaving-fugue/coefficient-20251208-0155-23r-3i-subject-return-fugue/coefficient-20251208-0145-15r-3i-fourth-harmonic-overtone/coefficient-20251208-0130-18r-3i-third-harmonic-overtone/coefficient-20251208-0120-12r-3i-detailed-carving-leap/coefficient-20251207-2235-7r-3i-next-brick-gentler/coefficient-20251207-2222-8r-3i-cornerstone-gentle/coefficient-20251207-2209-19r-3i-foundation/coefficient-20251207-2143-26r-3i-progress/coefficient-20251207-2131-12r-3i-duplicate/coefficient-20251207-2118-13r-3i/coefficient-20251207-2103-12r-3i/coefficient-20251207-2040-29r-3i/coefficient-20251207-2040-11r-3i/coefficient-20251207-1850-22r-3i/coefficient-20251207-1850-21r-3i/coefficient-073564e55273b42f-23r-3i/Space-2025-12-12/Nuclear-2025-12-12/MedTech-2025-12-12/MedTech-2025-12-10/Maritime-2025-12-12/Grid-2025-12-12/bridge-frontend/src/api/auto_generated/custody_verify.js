// AUTO-GEN-BRIDGE v1.7.0 - MODERATE
// Route: /custody/verify

import apiClient from '../api';

/**
 * Auto-generated API client for /custody/verify
 * Severity: moderate
 * @param {void} 
 */
export async function custody_verify() {
  try {
    const url = `/custody/verify`;
    const response = await apiClient.get(url);
    return response;
  } catch (error) {
    console.error('Error calling /custody/verify:', error);
    throw error;
  }
}
