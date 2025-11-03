// bridge-deploy.js
// Netlify Function to trigger your Bridge Runtime Handler node

export async function handler(event) {
  const forgeAuth = process.env.FORGE_DOMINION_ROOT;

  if (!event.headers.authorization || event.headers.authorization !== `Bearer ${forgeAuth}`) {
    return {
      statusCode: 403,
      body: JSON.stringify({ error: "Forbidden: invalid token" }),
    };
  }

  try {
    const payload = JSON.parse(event.body || "{}");
    const branch = payload?.branch || "main";
    const repo = payload?.repository || "kswhitlock9493-jpg/SR-AIbridge-";
    const image = `ghcr.io/${repo}/sr-aibridge-backend:latest`;

    const res = await fetch("http://localhost:7878/deploy", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${forgeAuth}`,
      },
      body: JSON.stringify({
        image,
        branch,
        timestamp: Date.now(),
      }),
    });

    const data = await res.json().catch(() => ({}));
    console.log("Bridge deploy hook:", data);

    return {
      statusCode: 200,
      body: JSON.stringify({ ok: true, data }),
    };
  } catch (err) {
    console.error("Bridge deploy error:", err);
    return {
      statusCode: 500,
      body: JSON.stringify({ ok: false, error: err.message }),
    };
  }
}
