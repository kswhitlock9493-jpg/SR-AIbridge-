// Netlify Function: System Health endpoint
// GET /.netlify/functions/api-system-health
export default async function handler(_request, _context) {
  return new Response(
    JSON.stringify({
      status: "healthy",
      uptime: "99.9%",
      cpuUsage: 45,
      memoryUsage: 62,
      diskUsage: 38,
      checks: {
        database: "healthy",
        api: "healthy",
        workers: "healthy"
      }
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
