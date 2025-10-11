// AUTO-GEN-BRIDGE v1.7.0 - MODERATE
// Route: /console/snapshot

import apiClient from '../api';

/**
 * Auto-generated API client for /console/snapshot
 * Severity: moderate
 * @param {void} 
 */
export async function console_snapshot() {
  try {
    const url = `/console/snapshot`;
    const response = await apiClient.get(url);
    return response;
  } catch (error) {
    console.error('Error calling /console/snapshot:', error);
    throw error;
  }
}
