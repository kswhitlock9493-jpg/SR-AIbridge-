// AUTO-GEN-BRIDGE v1.7.0 - MODERATE
// Route: /protocols/{name}/activate
// TODO: Review and integrate this auto-generated stub

import apiClient from '../api';

/**
 * Auto-generated API client for /protocols/{name}/activate
 * Severity: moderate
 * @param {name} 
 */
export async function protocols_name_activate(name) {
  try {
    const url = `/protocols/${name}/activate`;
    const response = await apiClient.get(url);
    return response;
  } catch (error) {
    console.error('Error calling /protocols/{name}/activate:', error);
    throw error;
  }
}
