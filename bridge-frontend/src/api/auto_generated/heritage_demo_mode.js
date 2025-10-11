// AUTO-GEN-BRIDGE v1.7.0 - MODERATE
// Route: /heritage/demo/{mode}

import apiClient from '../api';

/**
 * Auto-generated API client for /heritage/demo/{mode}
 * Severity: moderate
 * @param {mode} 
 */
export async function heritage_demo_mode(mode) {
  try {
    const url = `/heritage/demo/${mode}`;
    const response = await apiClient.get(url);
    return response;
  } catch (error) {
    console.error('Error calling /heritage/demo/{mode}:', error);
    throw error;
  }
}
