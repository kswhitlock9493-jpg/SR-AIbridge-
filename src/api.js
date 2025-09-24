const BASE_URL = "https://sr-aibridge.onrender.com";  // 👈 Render backend

// --- Core Status ---
export async function getStatus() {
  const res = await fetch(`${BASE_URL}/status`);
  if (!res.ok) throw new Error("Failed to fetch status");
  return res.json();
}

// --- Agents ---
export async function getAgents() {
  const res = await fetch(`${BASE_URL}/agents`);
  if (!res.ok) throw new Error("Failed to fetch agents");
  return res.json();
}

// --- Missions ---
export async function getMissions() {
  const res = await fetch(`${BASE_URL}/missions`);
  if (!res.ok) throw new Error("Failed to fetch missions");
  return res.json();
}

// --- Vault Logs / Doctrine ---
export async function getVaultLogs() {
  const res = await fetch(`${BASE_URL}/vault/logs`);
  if (!res.ok) throw new Error("Failed to fetch vault logs");
  return res.json();
}

// --- Captain-to-Captain Chat ---
export async function getCaptainMessages() {
  const res = await fetch(`${BASE_URL}/captains/messages`);
  if (!res.ok) throw new Error("Failed to fetch captain messages");
  return res.json();
}

export async function sendCaptainMessage(message) {
  const res = await fetch(`${BASE_URL}/captains/send`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
  });
  if (!res.ok) throw new Error("Failed to send message");
  return res.json();
}

// --- Armada ---
export async function getArmadaStatus() {
  const res = await fetch(`${BASE_URL}/armada/status`);
  if (!res.ok) throw new Error("Failed to fetch armada status");
  return res.json();
}

// --- Utilities ---
export async function reseedDemoData() {
  const res = await fetch(`${BASE_URL}/reseed`, { method: "POST" });
  if (!res.ok) throw new Error("Failed to reseed demo data");
  return res.json();
}