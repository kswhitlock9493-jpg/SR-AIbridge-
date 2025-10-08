// Netlify Function: Signed telemetry relay for agents & chat tools
// POST /.netlify/functions/telemetry  with JSON { type, status, details? }
// HMAC SHA256 signature in header: X-Bridge-Signature: sha256=...
import type { Handler } from "@netlify/functions";
import crypto from "node:crypto";

const json = (code: number, body: unknown) => ({
  statusCode: code,
  headers: { "content-type": "application/json" },
  body: JSON.stringify(body),
});

const verify = (secret: string, raw: string, sigHeader?: string) => {
  if (!sigHeader || !sigHeader.startsWith("sha256=")) return false;
  const their = sigHeader.split("sha256=")[1];
  const ours = crypto.createHmac("sha256", secret).update(raw).digest("hex");
  return crypto.timingSafeEqual(Buffer.from(ours), Buffer.from(their));
};

export const handler: Handler = async (evt) => {
  if (evt.httpMethod !== "POST") return json(405, { error: "Method Not Allowed" });
  const secret = process.env.TELEMETRY_SIGNING_SECRET;
  if (!secret) return json(500, { error: "Missing TELEMETRY_SIGNING_SECRET" });

  const raw = evt.body || "";
  const sig = evt.headers["x-bridge-signature"] || evt.headers["X-Bridge-Signature"];
  if (!verify(secret, raw, String(sig))) return json(401, { error: "Bad signature" });

  const webhook = process.env.DIAGNOSTICS_WEBHOOK_URL;
  if (!webhook) return json(500, { error: "Missing DIAGNOSTICS_WEBHOOK_URL" });

  // Fan-out to your diagnostics channel (Slack/Discord/Custom)
  await fetch(webhook, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: raw,
  });

  return json(200, { ok: true });
};
