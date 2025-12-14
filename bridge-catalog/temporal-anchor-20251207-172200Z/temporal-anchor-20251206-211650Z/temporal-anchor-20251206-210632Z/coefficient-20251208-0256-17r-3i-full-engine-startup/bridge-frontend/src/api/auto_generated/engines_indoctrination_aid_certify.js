// AUTO-GEN-BRIDGE v1.7.0 - MODERATE
// Route: /engines/indoctrination/{aid}/certify

import apiClient from '../api';

/**
 * Auto-generated API client for /engines/indoctrination/{aid}/certify
 * Severity: moderate
 * @param {aid} 
 */
export async function engines_indoctrination_aid_certify(aid) {
  try {
    const url = `/engines/indoctrination/${aid}/certify`;
    const response = await apiClient.get(url);
    return response;
  } catch (error) {
    console.error('Error calling /engines/indoctrination/{aid}/certify:', error);
    throw error;
  }
}
