// AUTO-GEN-BRIDGE v1.7.0 - MODERATE
// Route: /engines/speech/stt

import apiClient from '../api';

/**
 * Auto-generated API client for /engines/speech/stt
 * Severity: moderate
 * @param {void} 
 */
export async function engines_speech_stt() {
  try {
    const url = `/engines/speech/stt`;
    const response = await apiClient.get(url);
    return response;
  } catch (error) {
    console.error('Error calling /engines/speech/stt:', error);
    throw error;
  }
}
