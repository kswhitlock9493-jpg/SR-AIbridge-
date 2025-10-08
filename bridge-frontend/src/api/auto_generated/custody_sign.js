// AUTO-GEN-BRIDGE v1.7.0 - MODERATE
// Route: /custody/sign
// TODO: Review and integrate this auto-generated stub

import apiClient from '../api';

/**
 * Auto-generated API client for /custody/sign
 * Severity: moderate
 * @param {void} 
 */
export async function custody_sign() {
  try {
    const url = `/custody/sign`;
    const response = await apiClient.get(url);
    return response;
  } catch (error) {
    console.error('Error calling /custody/sign:', error);
    throw error;
  }
}
