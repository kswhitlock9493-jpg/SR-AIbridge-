import config from "./config";

export async function getStatus() {
  const res = await fetch(`${config.API_BASE_URL}/status`);
  if (!res.ok) throw new Error(`Status fetch failed: ${res.statusText}`);
  return res.json();
}

export async function getVaultLogs() {
  const res = await fetch(`${config.API_BASE_URL}/vault/logs`);
  if (!res.ok) throw new Error(`Vault logs fetch failed: ${res.statusText}`);
  return res.json();
}

export async function getMissionLog() {
  const res = await fetch(`${config.API_BASE_URL}/missions`);
  if (!res.ok) throw new Error(`Mission log fetch failed: ${res.statusText}`);
  return res.json();
}

export async function getChatMessages() {
  const res = await fetch(`${config.API_BASE_URL}/chat/messages`);
  if (!res.ok) throw new Error(`Chat fetch failed: ${res.statusText}`);
  return res.json();
}

export async function postChatMessage(author, message) {
  const res = await fetch(`${config.API_BASE_URL}/chat/send`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ author, message }),
  });
  if (!res.ok) throw new Error(`Chat send failed: ${res.statusText}`);
  return res.json();
}