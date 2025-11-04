// forge-resolver.js
// Forge Dominion Manifest Resolver
// Handles runtime handshake requests and returns ephemeral connection data

import crypto from "crypto";

// Global state for consensus tracking
// WARNING: Serverless functions are stateless. These variables will be reset
// on cold starts and are NOT shared across function invocations or instances.
// For production deployments with multiple BRH nodes, replace with:
//   - External database (DynamoDB, Firestore, etc.)
//   - Distributed cache (Redis, Memcached)
//   - Persistent storage (S3, Cloud Storage)
// This in-memory state is suitable for:
//   - Development/testing
//   - Single-region deployments with low traffic
//   - Temporary leader tracking between consensus cycles
let currentLeader = null;
let consensusHistory = [];

/**
 * Main handler for Forge Dominion Manifest Resolver
 * Supports:
 *   GET /manifest/resolve?target=ledger
 *   POST /federation/heartbeat
 *   POST /federation/consensus
 *   GET /federation/leader
 */
export async function handler(event) {
  try {
    // Construct URL from event properties for better compatibility
    const url = event.rawUrl 
      ? new URL(event.rawUrl) 
      : new URL(`https://${event.headers.host}${event.path}`);
    
    // Handle federation consensus endpoint
    if (url.pathname.includes("/federation/consensus") && event.httpMethod === "POST") {
      return await handleConsensus(event);
    }
    
    // Handle federation leader query endpoint
    if (url.pathname.includes("/federation/leader") && event.httpMethod === "GET") {
      return await handleLeaderQuery(event);
    }
    
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
        available: ["/manifest/resolve", "/federation/heartbeat", "/federation/consensus", "/federation/leader"]
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

/**
 * Handle consensus election reports from BRH nodes
 */
async function handleConsensus(event) {
  const data = JSON.parse(event.body || "{}");
  const { leader, peers, epoch } = data;

  console.log(`👑 Consensus report: Leader=${leader} | Peers=${peers?.length || 0} @ ${epoch}`);

  // Update current leader
  currentLeader = leader;
  
  // Store consensus history (keep last 100 entries)
  consensusHistory.push({
    epoch,
    leader,
    peers,
    timestamp: Date.now()
  });
  if (consensusHistory.length > 100) {
    consensusHistory.shift();
  }

  // Optionally forward to ledger for audit trail
  const ledgerForward = process.env.FORGE_CONSENSUS_LEDGER_FORWARD === "true";
  if (ledgerForward) {
    try {
      await fetch("https://sovereign.bridge/api/consensus", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ epoch, leader, peers }),
      });
    } catch (err) {
      console.log("ℹ️  Consensus ledger forward failed:", err.message);
    }
  }

  return { 
    statusCode: 200,
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ 
      ok: true,
      leader,
      peers_count: peers?.length || 0
    })
  };
}

/**
 * Handle leader query requests from BRH nodes
 */
async function handleLeaderQuery(event) {
  return {
    statusCode: 200,
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      leader: currentLeader,
      lease: null,  // Optional: implement lease token system
      epoch: Math.floor(Date.now() / 1000)
    })
  };
}
