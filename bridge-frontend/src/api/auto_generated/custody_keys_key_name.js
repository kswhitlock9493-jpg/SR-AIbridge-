// AUTO-GEN-BRIDGE v1.7.0 - MODERATE
// Route: /custody/keys/{key_name}
// TODO: Review and integrate this auto-generated stub

import apiClient from '../api';

/**
 * Auto-generated API client for /custody/keys/{key_name}
 * Severity: moderate
 * @param {key_name} 
 */
export async function custody_keys_key_name(key_name) {
  try {
    const url = `/custody/keys/{key_name}`;
    const response = await apiClient.get(url);
    return response;
  } catch (error) {
    console.error('Error calling /custody/keys/{key_name}:', error);
    throw error;
  }
}
