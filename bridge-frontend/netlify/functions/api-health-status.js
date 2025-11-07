// Netlify Function: Health Status endpoint  
// GET /.netlify/functions/api-health-status
// Maps to backend: /api/health/status
export default async function handler(_request, _context) {
  return new Response(
    JSON.stringify({
      status: "OK",
      uptime: 0,
      timestamp: new Date().toISOString()
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
