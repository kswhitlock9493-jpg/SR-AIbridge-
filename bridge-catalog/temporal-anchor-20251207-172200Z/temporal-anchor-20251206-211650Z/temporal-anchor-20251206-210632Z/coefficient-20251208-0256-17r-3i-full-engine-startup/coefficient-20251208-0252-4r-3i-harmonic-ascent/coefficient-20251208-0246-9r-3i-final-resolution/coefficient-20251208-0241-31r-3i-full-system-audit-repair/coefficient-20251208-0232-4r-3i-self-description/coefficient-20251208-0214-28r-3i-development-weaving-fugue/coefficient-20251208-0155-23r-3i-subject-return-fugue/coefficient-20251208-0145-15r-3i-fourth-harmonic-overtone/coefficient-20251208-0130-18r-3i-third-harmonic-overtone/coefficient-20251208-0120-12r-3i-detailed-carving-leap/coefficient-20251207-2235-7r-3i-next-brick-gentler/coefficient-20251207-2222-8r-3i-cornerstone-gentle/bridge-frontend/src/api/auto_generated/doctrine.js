// AUTO-GEN-BRIDGE v1.7.0 - MODERATE
// Route: /doctrine

import apiClient from '../api';

/**
 * Auto-generated API client for /doctrine
 * Severity: moderate
 * @param {void} 
 */
export async function doctrine() {
  try {
    const url = `/doctrine`;
    const response = await apiClient.get(url);
    return response;
  } catch (error) {
    console.error('Error calling /doctrine:', error);
    throw error;
  }
}
