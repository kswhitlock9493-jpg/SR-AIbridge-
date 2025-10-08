// AUTO-GEN-BRIDGE v1.7.0 - MODERATE
// Route: /custody/keys/{key_name}/generate
// TODO: Review and integrate this auto-generated stub

import apiClient from '../api';

/**
 * Auto-generated API client for /custody/keys/{key_name}/generate
 * Severity: moderate
 * @param {key_name} 
 */
export async function custody_keys_key_name_generate(key_name) {
  try {
    const url = `/custody/keys/{key_name}/generate`;
    const response = await apiClient.get(url);
    return response;
  } catch (error) {
    console.error('Error calling /custody/keys/{key_name}/generate:', error);
    throw error;
  }
}
