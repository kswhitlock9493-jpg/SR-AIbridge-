// AUTO-GEN-BRIDGE v1.7.0 - MODERATE
// Route: /system/repair

import apiClient from '../api';

/**
 * Auto-generated API client for /system/repair
 * Severity: moderate
 * @param {void} 
 */
export async function system_repair() {
  try {
    const url = `/system/repair`;
    const response = await apiClient.get(url);
    return response;
  } catch (error) {
    console.error('Error calling /system/repair:', error);
    throw error;
  }
}
