// forge-resolver.js
// Forge Dominion Manifest Resolver
// Handles runtime handshake requests and returns ephemeral connection data

import crypto from "crypto";

/**
 * Main handler for Forge Dominion Manifest Resolver
 * Supports:
 *   GET /manifest/resolve?target=ledger
 *   POST /federation/heartbeat
 */
export async function handler(event) {
  try {
    // Construct URL from event properties for better compatibility
    const url = event.rawUrl 
      ? new URL(event.rawUrl) 
      : new URL(`https://${event.headers.host}${event.path}`);
    
    // Handle federation heartbeat endpoint
    if (url.pathname.includes("/federation/heartbeat") && event.httpMethod === "POST") {
      return await handleHeartbeat(event);
    }
    
    // Handle manifest resolution endpoint
    if (url.pathname.includes("/manifest/resolve")) {
      return await handleManifestResolve(event, url);
    }
    
    // Default: return forge status
    return {
      statusCode: 404,
      body: JSON.stringify({
        error: "Unknown endpoint",
        available: ["/manifest/resolve", "/federation/heartbeat"]
      })
    };
    
  } catch (err) {
    console.error("❌ Forge resolver error:", err);
    return {
      statusCode: 500,
      body: JSON.stringify({ 
        error: "Forge resolver internal error",
        message: err.message 
      })
    };
  }
}

/**
 * Handle manifest resolution requests
 */
async function handleManifestResolve(event, url) {
  const target = url.searchParams.get("target") || "default";
  const epoch = Math.floor(Date.now() / 1000);

  // Generate short-lived signature using Dominion Seal
  const dominionSeal = process.env.DOMINION_SEAL || "forge-ephemeral";
  const sig = crypto
    .createHmac("sha256", dominionSeal)
    .update(`${target}:${epoch}`)
    .digest("hex")
    .slice(0, 32);

  // Target-based resolver routing
  const manifestMap = {
    ledger: {
      ledger_url: "https://sovereign.bridge/api/log",
      ledger_signature: sig,
      ledger_identity: "SR-AIBRIDGE::FORGE::EPOCH-" + epoch,
    },
    bridge: {
      bridge_url: "https://sr-aibridge.netlify.app/.netlify/functions/bridge-deploy",
      bridge_signature: sig,
      bridge_identity: "SR-AIBRIDGE::FORGE::LIVE",
    },
    default: {
      forge_status: "active",
      forge_epoch: epoch,
      forge_sig: sig,
    },
  };

  const response = manifestMap[target] || manifestMap.default;

  return {
    statusCode: 200,
    headers: {
      "Content-Type": "application/json",
      "Cache-Control": "no-store, no-cache, must-revalidate"
    },
    body: JSON.stringify({
      forge_root: process.env.FORGE_DOMINION_ROOT || "dominion://sovereign.bridge",
      epoch,
      target,
      ...response,
    }),
  };
}

/**
 * Handle federation heartbeat requests
 */
async function handleHeartbeat(event) {
  const pulse = JSON.parse(event.body || "{}");
  const now = Math.floor(Date.now() / 1000);
  const age = now - pulse.epoch;
  const valid = age < 300; // 5-minute tolerance

  if (valid) {
    console.log(`💓 Heartbeat from ${pulse.node} @ ${pulse.epoch}`);
  } else {
    console.warn(`⚠️  Stale heartbeat from ${pulse.node} (age: ${age}s)`);
  }

  // Optionally forward to Sovereign Ledger
  const forwardToLedger = process.env.FORGE_HEARTBEAT_LEDGER_FORWARD === "true";
  if (forwardToLedger) {
    try {
      await fetch("https://sovereign.bridge/api/pulse", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(pulse),
      });
    } catch (err) {
      console.log("ℹ️  Ledger forward failed:", err.message);
    }
  }

  return { 
    statusCode: 200,
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ 
      ok: true,
      valid,
      age,
      received_at: now
    })
  };
}
