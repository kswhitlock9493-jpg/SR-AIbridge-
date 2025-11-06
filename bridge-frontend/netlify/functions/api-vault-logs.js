// Netlify Function: Vault Logs endpoint
// GET /.netlify/functions/api-vault-logs
export default async function handler(_request, _context) {
  return new Response(
    JSON.stringify({
      logs: [
        {
          id: "log-001",
          timestamp: new Date(Date.now() - 3600000).toISOString(),
          event: "Key rotation completed",
          severity: "info"
        },
        {
          id: "log-002",
          timestamp: new Date(Date.now() - 7200000).toISOString(),
          event: "Backup created successfully",
          severity: "info"
        },
        {
          id: "log-003",
          timestamp: new Date(Date.now() - 10800000).toISOString(),
          event: "Access granted: Admiral",
          severity: "info"
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
