// AUTO-GEN-BRIDGE v1.7.0 - MODERATE
// Route: /heritage/demo/modes

import apiClient from '../api';

/**
 * Auto-generated API client for /heritage/demo/modes
 * Severity: moderate
 * @param {void} 
 */
export async function heritage_demo_modes() {
  try {
    const url = `/heritage/demo/modes`;
    const response = await apiClient.get(url);
    return response;
  } catch (error) {
    console.error('Error calling /heritage/demo/modes:', error);
    throw error;
  }
}
