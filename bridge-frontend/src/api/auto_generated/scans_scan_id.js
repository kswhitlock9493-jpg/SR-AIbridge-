// AUTO-GEN-BRIDGE v1.7.0 - MODERATE
// Route: /scans/{scan_id}
// TODO: Review and integrate this auto-generated stub

import apiClient from '../api';

/**
 * Auto-generated API client for /scans/{scan_id}
 * Severity: moderate
 * @param {scan_id} 
 */
export async function scans_scan_id(scan_id) {
  try {
    const url = `/scans/${scan_id}`;
    const response = await apiClient.get(url);
    return response;
  } catch (error) {
    console.error('Error calling /scans/{scan_id}:', error);
    throw error;
  }
}
