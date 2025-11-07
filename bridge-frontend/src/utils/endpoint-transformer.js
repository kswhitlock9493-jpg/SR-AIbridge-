/**
 * Endpoint Transformer Utility
 * Handles transformation of API endpoints for different deployment modes
 */

import config from '../config';

// Map endpoint paths to Netlify Function names (when using Netlify Functions)
const NETLIFY_ENDPOINT_MAP = {
  '/status': '/api-status',
  '/agents': '/api-agents',
  '/missions': '/api-missions',
  '/vault/logs': '/api-vault-logs',
  '/armada/status': '/api-armada-status',
  '/health': '/api-system-health',
  '/activity': '/api-activity',
  '/api/health/health': '/api-health',
  '/api/health/health/full': '/api-health-full',
  '/api/health/status': '/api-health-status',
  '/api/system/metrics': '/api-system-metrics',
  '/api/missions/missions': '/api-missions'
};

/**
 * Check if we're using Netlify Functions
 * @returns {boolean} True if using Netlify Functions
 */
export function isNetlifyFunctions() {
  const apiBase = config.API_BASE_URL;
  return apiBase && apiBase.includes('/.netlify/functions');
}

/**
 * Transform endpoint for Netlify Functions if needed
 * @param {string} endpoint - Original endpoint path
 * @returns {string} Transformed endpoint path
 */
export function transformEndpoint(endpoint) {
  // Only transform if using Netlify Functions
  if (!isNetlifyFunctions()) {
    return endpoint;
  }
  
  // For Netlify Functions, map the endpoint to the function name
  // First check exact matches
  if (NETLIFY_ENDPOINT_MAP[endpoint]) {
    return NETLIFY_ENDPOINT_MAP[endpoint];
  }
  
  // Check for partial matches (e.g., /missions?captain=x -> /api-missions?captain=x)
  // Need to handle query strings
  const [path, queryString] = endpoint.split('?');
  
  // Check if the path (without query) has a mapping
  if (NETLIFY_ENDPOINT_MAP[path]) {
    return queryString ? `${NETLIFY_ENDPOINT_MAP[path]}?${queryString}` : NETLIFY_ENDPOINT_MAP[path];
  }
  
  // Check for partial path matches
  for (const [key, value] of Object.entries(NETLIFY_ENDPOINT_MAP)) {
    if (path.startsWith(key)) {
      const transformed = path.replace(key, value);
      return queryString ? `${transformed}?${queryString}` : transformed;
    }
  }
  
  // Default: transform path to Netlify function name
  // Remove leading slash, replace remaining slashes with dashes
  // e.g., /users/profile -> /api-users-profile
  // BUT: Don't duplicate "api" if it's already there
  let transformedPath = path.startsWith('/') ? path.slice(1) : path;
  
  // If path already starts with "api/", just replace slashes with dashes
  if (transformedPath.startsWith('api/')) {
    transformedPath = `/${transformedPath.replace(/\//g, '-')}`;
  } else {
    // Otherwise, prepend "api-" and replace slashes with dashes
    transformedPath = `/api-${transformedPath.replace(/\//g, '-')}`;
  }
  
  return queryString ? `${transformedPath}?${queryString}` : transformedPath;
}

/**
 * Build full URL from endpoint
 * @param {string} endpoint - Endpoint path
 * @param {string} baseURL - Optional base URL override
 * @returns {string} Full URL
 */
export function buildURL(endpoint, baseURL = null) {
  const base = baseURL || config.API_BASE_URL;
  const transformed = transformEndpoint(endpoint);
  
  // If endpoint is already a full URL, return as-is
  if (transformed.startsWith('http://') || transformed.startsWith('https://')) {
    return transformed;
  }
  
  // If base is empty or just "/", return the transformed endpoint directly
  if (!base || base === '/' || base === '') {
    return transformed;
  }
  
  // If using Netlify Functions, base is already the /.netlify/functions path
  // Just append the transformed endpoint
  if (isNetlifyFunctions()) {
    return `${base}${transformed}`;
  }
  
  // Otherwise, append endpoint to base
  return `${base}${transformed}`;
}

export default {
  transformEndpoint,
  buildURL,
  isNetlifyFunctions,
  NETLIFY_ENDPOINT_MAP
};
