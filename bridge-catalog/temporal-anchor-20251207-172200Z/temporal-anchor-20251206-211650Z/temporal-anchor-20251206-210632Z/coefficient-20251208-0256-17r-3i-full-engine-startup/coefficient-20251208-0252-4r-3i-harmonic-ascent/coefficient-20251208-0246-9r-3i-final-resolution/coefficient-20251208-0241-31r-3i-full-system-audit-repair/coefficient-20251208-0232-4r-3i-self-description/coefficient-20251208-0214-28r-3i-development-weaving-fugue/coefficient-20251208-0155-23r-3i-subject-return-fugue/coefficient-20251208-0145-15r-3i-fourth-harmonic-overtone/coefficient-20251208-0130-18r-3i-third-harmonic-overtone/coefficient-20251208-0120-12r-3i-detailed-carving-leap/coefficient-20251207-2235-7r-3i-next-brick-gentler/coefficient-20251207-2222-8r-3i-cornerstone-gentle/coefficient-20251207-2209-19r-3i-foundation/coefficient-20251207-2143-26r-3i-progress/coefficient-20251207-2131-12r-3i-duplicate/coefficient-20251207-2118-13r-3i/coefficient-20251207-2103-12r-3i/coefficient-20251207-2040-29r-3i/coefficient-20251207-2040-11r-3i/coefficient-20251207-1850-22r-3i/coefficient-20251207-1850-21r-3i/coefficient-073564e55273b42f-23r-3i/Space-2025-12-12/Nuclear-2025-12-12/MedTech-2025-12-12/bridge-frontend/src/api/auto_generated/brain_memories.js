// AUTO-GEN-BRIDGE v1.7.0 - MODERATE
// Route: /brain/memories

import apiClient from '../api';

/**
 * Auto-generated API client for /brain/memories
 * Severity: moderate
 * @param {void} 
 */
export async function brain_memories() {
  try {
    const url = `/brain/memories`;
    const response = await apiClient.get(url);
    return response;
  } catch (error) {
    console.error('Error calling /brain/memories:', error);
    throw error;
  }
}
