// AUTO-GEN-BRIDGE v1.7.0 - MODERATE
// Route: /bridge-core/protocols/registry
// TODO: Review and integrate this auto-generated stub

import apiClient from '../api';

/**
 * Auto-generated API client for /bridge-core/protocols/registry
 * Severity: moderate
 * @param {void} 
 */
export async function bridge_core_protocols_registry() {
  try {
    const url = `/bridge-core/protocols/registry`;
    const response = await apiClient.get(url);
    return response;
  } catch (error) {
    console.error('Error calling /bridge-core/protocols/registry:', error);
    throw error;
  }
}
