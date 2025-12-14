// AUTO-GEN-BRIDGE v1.7.0 - MODERATE
// Route: /custody/init

import apiClient from '../api';

/**
 * Auto-generated API client for /custody/init
 * Severity: moderate
 * @param {void} 
 */
export async function custody_init() {
  try {
    const url = `/custody/init`;
    const response = await apiClient.get(url);
    return response;
  } catch (error) {
    console.error('Error calling /custody/init:', error);
    throw error;
  }
}
