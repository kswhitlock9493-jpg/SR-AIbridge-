// Netlify Function: Health probe for SR-AIbridge
// GET /.netlify/functions/health  -> JSON summary
import type { Handler } from "@netlify/functions";

const ok = async (url: string) => {
  try {
    const res = await fetch(url, { method: "GET", cache: "no-store" });
    return res.ok;
  } catch {
    return false;
  }
};

export const handler: Handler = async () => {
  const backend = process.env.RENDER_HEALTH_URL || "https://sr-aibridge.onrender.com/api/health";
  const frontend = process.env.FRONTEND_HEALTH_URL || "https://sr-aibridge.netlify.app";
  const service = process.env.SITE_URL || "https://sr-aibridge.netlify.app";

  const backendOk = await ok(backend);
  const frontendOk = await ok(frontend);

  const status = backendOk && frontendOk ? "stable" : "degraded";
  const code = status === "stable" ? 200 : 503;

  return {
    statusCode: code,
    headers: { "content-type": "application/json" },
    body: JSON.stringify({
      service,
      backend: { url: backend, ok: backendOk },
      frontend: { url: frontend, ok: frontendOk },
      status,
      ts: new Date().toISOString(),
    }),
  };
};
