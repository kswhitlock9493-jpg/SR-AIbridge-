// AUTO-GEN-BRIDGE v1.7.0 - MODERATE
// Route: /registry/tier/me
// TODO: Review and integrate this auto-generated stub

import apiClient from '../api';

/**
 * Auto-generated API client for /registry/tier/me
 * Severity: moderate
 * @param {void} 
 */
export async function registry_tier_me() {
  try {
    const url = `/registry/tier/me`;
    const response = await apiClient.get(url);
    return response;
  } catch (error) {
    console.error('Error calling /registry/tier/me:', error);
    throw error;
  }
}
