// Centralized environment gateway
// Default to localhost for BRH (Bridge Runtime Handler) development
export const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";
export const BRIDGE_API_URL = import.meta.env.BRIDGE_API_URL || API_BASE;
export const CASCADE_MODE = import.meta.env.CASCADE_MODE || "active";
export const VAULT_URL = import.meta.env.VAULT_URL || "https://vault.sr-aibridge.com";

const config = {
  // API Base URL - uses import.meta.env to prevent inlining secrets into dist
  API_BASE_URL: API_BASE,
  
  // WebSocket Base URL for real-time updates
  WS_BASE_URL: import.meta.env.VITE_WS_BASE ||
    (import.meta.env.MODE === 'development'
      ? "ws://localhost:8000"
      : "ws://localhost:8000")  // BRH WebSocket endpoint
};

export default config;
