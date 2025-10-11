// AUTO-GEN-BRIDGE v1.7.0 - MODERATE
// Route: /engines/recovery/dispatch-and-ingest

import apiClient from '../api';

/**
 * Auto-generated API client for /engines/recovery/dispatch-and-ingest
 * Severity: moderate
 * @param {void} 
 */
export async function engines_recovery_dispatch_and_ingest() {
  try {
    const url = `/engines/recovery/dispatch-and-ingest`;
    const response = await apiClient.post(url);
    return response;
  } catch (error) {
    console.error('Error calling /engines/recovery/dispatch-and-ingest:', error);
    throw error;
  }
}
