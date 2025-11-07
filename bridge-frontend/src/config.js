// Centralized environment gateway
// Production-first configuration with development fallback

// Determine API base URL with proper precedence:
// 1. VITE_API_BASE (Vite standard) - highest priority
// 2. REACT_APP_API_URL (React standard, supported via vite.config.js)
// 3. Production default based on deployment type
// 4. Localhost for development mode
const getApiBase = () => {
  // Check for explicit environment variables
  if (import.meta.env.VITE_API_BASE) {
    return import.meta.env.VITE_API_BASE;
  }
  if (import.meta.env.REACT_APP_API_URL) {
    return import.meta.env.REACT_APP_API_URL;
  }
  
  // Production vs development defaults
  if (import.meta.env.MODE === 'development') {
    return "http://localhost:8000";
  }
  
  // Production default:
  // If backend is deployed separately (e.g., Render, BRH), API calls should go directly to it
  // The backend URL should be set via VITE_API_BASE environment variable in Netlify
  // For now, default to empty string (relative paths) which will work if backend is proxied
  // via _redirects or if backend is on same domain
  return "";
};

export const API_BASE = getApiBase();
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
      : API_BASE.replace('https://', 'wss://').replace('http://', 'ws://'))
};

export default config;
