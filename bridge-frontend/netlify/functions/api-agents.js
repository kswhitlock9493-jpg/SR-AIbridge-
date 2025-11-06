// Netlify Function: Agents endpoint
// GET /.netlify/functions/api-agents
export default async function handler(request, context) {
  return new Response(
    JSON.stringify({
      agents: [
        {
          id: "agent-001",
          name: "Forge Agent",
          status: "online",
          type: "forge",
          lastSeen: new Date().toISOString()
        },
        {
          id: "agent-002",
          name: "Bridge Agent",
          status: "online",
          type: "bridge",
          lastSeen: new Date().toISOString()
        },
        {
          id: "agent-003",
          name: "Sovereign Agent",
          status: "online",
          type: "sovereign",
          lastSeen: new Date().toISOString()
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
