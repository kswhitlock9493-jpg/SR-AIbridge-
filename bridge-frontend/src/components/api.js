export async function getStatus() {
  const response = await fetch("http://localhost:8000/status");
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return await response.json();
}