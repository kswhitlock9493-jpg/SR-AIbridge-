// AUTO-GEN-BRIDGE v1.7.0 - MODERATE
// Route: /brain/categories

import apiClient from '../api';

/**
 * Auto-generated API client for /brain/categories
 * Severity: moderate
 * @param {void} 
 */
export async function brain_categories() {
  try {
    const url = `/brain/categories`;
    const response = await apiClient.get(url);
    return response;
  } catch (error) {
    console.error('Error calling /brain/categories:', error);
    throw error;
  }
}
