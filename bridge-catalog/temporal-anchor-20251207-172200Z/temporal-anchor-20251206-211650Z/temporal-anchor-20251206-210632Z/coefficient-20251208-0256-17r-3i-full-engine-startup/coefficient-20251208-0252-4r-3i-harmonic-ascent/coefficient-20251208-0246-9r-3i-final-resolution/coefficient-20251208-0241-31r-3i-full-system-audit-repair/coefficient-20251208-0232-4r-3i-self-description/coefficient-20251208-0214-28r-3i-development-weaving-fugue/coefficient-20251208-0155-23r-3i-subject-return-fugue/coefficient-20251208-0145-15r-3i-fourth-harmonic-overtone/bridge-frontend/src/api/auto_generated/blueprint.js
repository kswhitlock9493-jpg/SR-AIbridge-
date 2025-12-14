// AUTO-GEN-BRIDGE v1.7.0 - MODERATE
// Route: /blueprint/

import apiClient from '../api';

/**
 * Auto-generated API client for /blueprint/
 * Severity: moderate
 * @param {void} 
 */
export async function blueprint() {
  try {
    const url = `/blueprint/`;
    const response = await apiClient.get(url);
    return response;
  } catch (error) {
    console.error('Error calling /blueprint/:', error);
    throw error;
  }
}
