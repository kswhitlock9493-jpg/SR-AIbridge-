// AUTO-GEN-BRIDGE v1.7.0 - MODERATE
// Route: /bridge-core/protocols/{name}/lore
// TODO: Review and integrate this auto-generated stub

import apiClient from '../api';

/**
 * Auto-generated API client for /bridge-core/protocols/{name}/lore
 * Severity: moderate
 * @param {name} 
 */
export async function bridge_core_protocols_name_lore(name) {
  try {
    const url = `/bridge-core/protocols/{name}/lore`;
    const response = await apiClient.get(url);
    return response;
  } catch (error) {
    console.error('Error calling /bridge-core/protocols/{name}/lore:', error);
    throw error;
  }
}
