// AUTO-GEN-BRIDGE v1.7.0 - MODERATE
// Route: /brain/verify

import apiClient from '../api';

/**
 * Auto-generated API client for /brain/verify
 * Severity: moderate
 * @param {void} 
 */
export async function brain_verify() {
  try {
    const url = `/brain/verify`;
    const response = await apiClient.get(url);
    return response;
  } catch (error) {
    console.error('Error calling /brain/verify:', error);
    throw error;
  }
}
