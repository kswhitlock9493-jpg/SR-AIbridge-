// AUTO-GEN-BRIDGE v1.7.0 - MODERATE
// Route: /permissions/tiers/{tier_name}
// TODO: Review and integrate this auto-generated stub

import apiClient from '../api';

/**
 * Auto-generated API client for /permissions/tiers/{tier_name}
 * Severity: moderate
 * @param {tier_name} 
 */
export async function permissions_tiers_tier_name(tier_name) {
  try {
    const url = `/permissions/tiers/${tier_name}`;
    const response = await apiClient.get(url);
    return response;
  } catch (error) {
    console.error('Error calling /permissions/tiers/{tier_name}:', error);
    throw error;
  }
}
