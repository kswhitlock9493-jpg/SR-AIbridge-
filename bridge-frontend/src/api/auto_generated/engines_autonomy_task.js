// AUTO-GEN-BRIDGE v1.7.0 - MODERATE
// Route: /engines/autonomy/task

import apiClient from '../api';

/**
 * Auto-generated API client for /engines/autonomy/task
 * Severity: moderate
 * @param {void} 
 */
export async function engines_autonomy_task() {
  try {
    const url = `/engines/autonomy/task`;
    const response = await apiClient.get(url);
    return response;
  } catch (error) {
    console.error('Error calling /engines/autonomy/task:', error);
    throw error;
  }
}
