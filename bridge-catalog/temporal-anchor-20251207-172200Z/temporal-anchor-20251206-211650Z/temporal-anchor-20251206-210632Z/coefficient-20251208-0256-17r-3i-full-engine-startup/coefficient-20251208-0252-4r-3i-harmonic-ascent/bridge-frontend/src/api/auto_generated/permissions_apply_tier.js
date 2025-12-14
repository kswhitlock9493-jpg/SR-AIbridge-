// AUTO-GEN-BRIDGE v1.7.0 - MODERATE
// Route: /permissions/apply-tier

import apiClient from '../api';

/**
 * Auto-generated API client for /permissions/apply-tier
 * Severity: moderate
 * @param {void} 
 */
export async function permissions_apply_tier() {
  try {
    const url = `/permissions/apply-tier`;
    const response = await apiClient.put(url);
    return response;
  } catch (error) {
    console.error('Error calling /permissions/apply-tier:', error);
    throw error;
  }
}
