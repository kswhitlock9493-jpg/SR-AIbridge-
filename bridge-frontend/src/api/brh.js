// BRH (Bridge Runtime Handler) API Client
// Centralized API functions for communicating with BRH backend

const BASE = import.meta.env.VITE_API_BASE || "/.netlify/functions/brh";

/**
 * Generic API request helper with error handling
 * @template T
 * @param {string} path - API endpoint path (e.g., "/health", "/genesis/heartbeat")
 * @param {RequestInit} init - Fetch options
 * @returns {Promise<T>} Response data
 */
export async function api(path, init = {}) {
  const res = await fetch(`${BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init.headers || {}),
    },
  });
  if (!res.ok) throw new Error(`API ${path} failed: ${res.status}`);
  return res.json();
}

/**
 * Check if BRH backend is alive and responsive
 * @returns {Promise<boolean>} True if backend is healthy
 */
export async function ensureLiveBackend() {
  try {
    const r = await api("/health");
    return r?.status === "ok";
  } catch {
    return false;
  }
}

/**
 * Ping BRH to confirm it's ready (genesis heartbeat)
 * @returns {Promise<{bridge: string, brh: string}>}
 */
export async function genesisHeartbeat() {
  return api("/genesis/heartbeat", { method: "POST" });
}

/**
 * Trigger BRH self-heal operation
 * @returns {Promise<{status: string, op: string}>}
 */
export async function triggerSelfHeal() {
  return api("/triage/self-heal", { method: "POST" });
}

/**
 * Execute a workflow on BRH
 * @param {string} name - Workflow name
 * @param {object} [payload] - Optional workflow payload
 * @returns {Promise<{accepted: boolean, workflow: string}>}
 */
export async function executeWorkflow(name, payload = null) {
  return api("/workflows/execute", {
    method: "POST",
    body: JSON.stringify({ name, payload }),
  });
}
