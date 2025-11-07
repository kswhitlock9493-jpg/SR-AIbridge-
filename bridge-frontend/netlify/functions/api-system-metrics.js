// Netlify Function: System Metrics endpoint
// GET /.netlify/functions/api-system-metrics
// Maps to backend: /api/system/metrics
export default async function handler(_request, _context) {
  return new Response(
    JSON.stringify({
      timestamp: new Date().toISOString(),
      uptime: "mock-uptime",
      requests: { total: 0, errors: 0 }
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
