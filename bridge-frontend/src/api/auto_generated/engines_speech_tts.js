// AUTO-GEN-BRIDGE v1.7.0 - MODERATE
// Route: /engines/speech/tts

import apiClient from '../api';

/**
 * Auto-generated API client for /engines/speech/tts
 * Severity: moderate
 * @param {void} 
 */
export async function engines_speech_tts() {
  try {
    const url = `/engines/speech/tts`;
    const response = await apiClient.get(url);
    return response;
  } catch (error) {
    console.error('Error calling /engines/speech/tts:', error);
    throw error;
  }
}
