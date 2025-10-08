// AUTO-GEN-BRIDGE v1.7.0 - MODERATE
// Route: /blueprint/{bp_id}
// TODO: Review and integrate this auto-generated stub

import apiClient from '../api';

/**
 * Auto-generated API client for /blueprint/{bp_id}
 * Severity: moderate
 * @param {bp_id} 
 */
export async function blueprint_bp_id(bp_id) {
  try {
    const url = `/blueprint/{bp_id}`;
    const response = await apiClient.get(url);
    return response;
  } catch (error) {
    console.error('Error calling /blueprint/{bp_id}:', error);
    throw error;
  }
}
