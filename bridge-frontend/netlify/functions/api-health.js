// Netlify Function: Health Check endpoint
// GET /.netlify/functions/api-health
// Maps to backend: /api/health/health
export default async function handler(_request, _context) {
  return new Response(
    JSON.stringify({
      status: "ok",
      host: "netlify",
      message: "Bridge link established and synchronized",
      service: "SR-AIbridge",
      version: "2.0.0",
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
