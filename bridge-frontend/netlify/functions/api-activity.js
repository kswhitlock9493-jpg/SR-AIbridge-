// Netlify Function: Activity endpoint
// GET /.netlify/functions/api-activity
export default async function handler(_request, _context) {
  const now = Date.now();
  return new Response(
    JSON.stringify({
      activity: [
        {
          id: "act-001",
          timestamp: new Date(now - 300000).toISOString(),
          time: "5m ago",
          description: "Agent connected: Forge Agent"
        },
        {
          id: "act-002",
          timestamp: new Date(now - 600000).toISOString(),
          time: "10m ago",
          description: "Mission started: UI Dashboard Integration"
        },
        {
          id: "act-003",
          timestamp: new Date(now - 900000).toISOString(),
          time: "15m ago",
          description: "System health check passed"
        },
        {
          id: "act-004",
          timestamp: new Date(now - 1800000).toISOString(),
          time: "30m ago",
          description: "Vault backup completed"
        }
      ]
    }),
    {
      status: 200,
      headers: {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type"
      }
    }
  );
}
