// AUTO-GEN-BRIDGE v1.7.0 - MODERATE
// Route: /protocols/{name}/vault

import apiClient from '../api';

/**
 * Auto-generated API client for /protocols/{name}/vault
 * Severity: moderate
 * @param {name} 
 */
export async function protocols_name_vault(name) {
  try {
    const url = `/protocols/${name}/vault`;
    const response = await apiClient.get(url);
    return response;
  } catch (error) {
    console.error('Error calling /protocols/{name}/vault:', error);
    throw error;
  }
}
