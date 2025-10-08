// AUTO-GEN-BRIDGE v1.7.0 - MODERATE
// Route: /engines/indoctrination/{aid}/revoke
// TODO: Review and integrate this auto-generated stub

import apiClient from '../api';

/**
 * Auto-generated API client for /engines/indoctrination/{aid}/revoke
 * Severity: moderate
 * @param {aid} 
 */
export async function engines_indoctrination_aid_revoke(aid) {
  try {
    const url = `/engines/indoctrination/{aid}/revoke`;
    const response = await apiClient.delete(url);
    return response;
  } catch (error) {
    console.error('Error calling /engines/indoctrination/{aid}/revoke:', error);
    throw error;
  }
}
