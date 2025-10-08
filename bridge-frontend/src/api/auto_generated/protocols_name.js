// AUTO-GEN-BRIDGE v1.7.0 - MODERATE
// Route: /protocols/{name}
// TODO: Review and integrate this auto-generated stub

import apiClient from '../api';

/**
 * Auto-generated API client for /protocols/{name}
 * Severity: moderate
 * @param {name} 
 */
export async function protocols_name(name) {
  try {
    const url = `/protocols/{name}`;
    const response = await apiClient.get(url);
    return response;
  } catch (error) {
    console.error('Error calling /protocols/{name}:', error);
    throw error;
  }
}
