// AUTO-GEN-BRIDGE v1.7.0 - MODERATE
// Route: /engines/autonomy/tasks
// TODO: Review and integrate this auto-generated stub

import apiClient from '../api';

/**
 * Auto-generated API client for /engines/autonomy/tasks
 * Severity: moderate
 * @param {void} 
 */
export async function engines_autonomy_tasks() {
  try {
    const url = `/engines/autonomy/tasks`;
    const response = await apiClient.get(url);
    return response;
  } catch (error) {
    console.error('Error calling /engines/autonomy/tasks:', error);
    throw error;
  }
}
