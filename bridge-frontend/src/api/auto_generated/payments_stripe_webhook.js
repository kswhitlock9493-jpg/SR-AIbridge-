// AUTO-GEN-BRIDGE v1.7.0 - MODERATE
// Route: /payments/stripe/webhook
// TODO: Review and integrate this auto-generated stub

import apiClient from '../api';

/**
 * Auto-generated API client for /payments/stripe/webhook
 * Severity: moderate
 * @param {void} 
 */
export async function payments_stripe_webhook() {
  try {
    const url = `/payments/stripe/webhook`;
    const response = await apiClient.get(url);
    return response;
  } catch (error) {
    console.error('Error calling /payments/stripe/webhook:', error);
    throw error;
  }
}
