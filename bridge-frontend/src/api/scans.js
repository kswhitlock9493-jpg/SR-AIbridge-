import config from "../config";

const API_BASE = config.API_BASE_URL;

export async function fetchScans() {
  const res = await fetch(`${API_BASE}/scans`);
  if (!res.ok) throw new Error("Failed to fetch scans");
  return res.json();
}

export async function fetchScan(scanId) {
  const res = await fetch(`${API_BASE}/scans/${scanId}`);
  if (!res.ok) throw new Error("Scan not found");
  return res.json();
}
