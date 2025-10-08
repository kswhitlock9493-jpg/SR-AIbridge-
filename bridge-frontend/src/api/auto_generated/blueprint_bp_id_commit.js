// AUTO-GEN-BRIDGE v1.7.0 - MODERATE
// Route: /blueprint/{bp_id}/commit
// TODO: Review and integrate this auto-generated stub

import apiClient from '../api';

/**
 * Auto-generated API client for /blueprint/{bp_id}/commit
 * Severity: moderate
 * @param {bp_id} 
 */
export async function blueprint_bp_id_commit(bp_id) {
  try {
    const url = `/blueprint/{bp_id}/commit`;
    const response = await apiClient.get(url);
    return response;
  } catch (error) {
    console.error('Error calling /blueprint/{bp_id}/commit:', error);
    throw error;
  }
}
