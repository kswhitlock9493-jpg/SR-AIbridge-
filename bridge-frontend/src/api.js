import config from './config';

const API_BASE_URL = config.API_BASE_URL;

export async function getStatus() {
  const response = await fetch(`${API_BASE_URL}/status`);
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }
  return await response.json();
}

export async function getAgents() {
  const response = await fetch(`${API_BASE_URL}/agents`);
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }
  return await response.json();
}

export async function getMissions() {
  const response = await fetch(`${API_BASE_URL}/missions`);
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }
  return await response.json();
}

export async function getVaultLogs() {
  const response = await fetch(`${API_BASE_URL}/vault/logs`);
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }
  return await response.json();
}

export async function getCaptainMessages() {
  const response = await fetch(`${API_BASE_URL}/captains/messages`);
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }
  return await response.json();
}

export async function sendCaptainMessage(message) {
  const response = await fetch(`${API_BASE_URL}/captains/send`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(message),
  });
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }
  return await response.json();
}

export async function getArmadaStatus() {
  const response = await fetch(`${API_BASE_URL}/armada/status`);
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }
  return await response.json();
}

export async function getActivity() {
  const response = await fetch(`${API_BASE_URL}/activity`);
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }
  return await response.json();
}

export async function createAgent(agent) {
  const response = await fetch(`${API_BASE_URL}/agents`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(agent),
  });
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }
  return await response.json();
}

export async function createMission(mission) {
  const response = await fetch(`${API_BASE_URL}/missions`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(mission),
  });
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }
  return await response.json();
}

export async function addVaultLog(log) {
  const response = await fetch(`${API_BASE_URL}/vault/logs`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(log),
  });
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }
  return await response.json();
}