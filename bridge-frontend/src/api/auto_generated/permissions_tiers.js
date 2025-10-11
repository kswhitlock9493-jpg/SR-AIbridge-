// AUTO-GEN-BRIDGE v1.7.0 - MODERATE
// Route: /permissions/tiers

import apiClient from '../api';

/**
 * Auto-generated API client for /permissions/tiers
 * Severity: moderate
 * @param {void} 
 */
export async function permissions_tiers() {
  try {
    const url = `/permissions/tiers`;
    const response = await apiClient.get(url);
    return response;
  } catch (error) {
    console.error('Error calling /permissions/tiers:', error);
    throw error;
  }
}
