// AUTO-GEN-BRIDGE v1.7.0 - MODERATE
// Route: /bridge-core/protocols/{name}

import apiClient from '../api';

/**
 * Auto-generated API client for /bridge-core/protocols/{name}
 * Severity: moderate
 * @param {name} 
 */
export async function bridge_core_protocols_name(name) {
  try {
    const url = `/bridge-core/protocols/${name}`;
    const response = await apiClient.get(url);
    return response;
  } catch (error) {
    console.error('Error calling /bridge-core/protocols/{name}:', error);
    throw error;
  }
}
