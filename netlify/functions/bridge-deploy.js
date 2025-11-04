// bridge-deploy.js
// Netlify Function to trigger your Bridge Runtime Handler node

export async function handler(event) {
  try {
    // Parse incoming deploy event
    const payload = JSON.parse(event.body || "{}");

    // Pull Forge credentials dynamically from the Dominion root
    const forgeRoot = process.env.FORGE_DOMINION_ROOT;
    if (!forgeRoot) {
      return { statusCode: 400, body: "Missing Forge Dominion Root" };
    }

    console.log("🔗 Bridge Received:", payload);

    // Forward event to GitHub as repository_dispatch
    const ghToken = process.env.GITHUB_TOKEN;
    if (ghToken) {
      try {
        const ghRes = await fetch("https://api.github.com/repos/kswhitlock9493-jpg/SR-AIbridge-/dispatches", {
          method: "POST",
          headers: {
            "Accept": "application/vnd.github+json",
            "Authorization": `Bearer ${ghToken}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            event_type: "bridge-deploy",
            client_payload: {
              status: payload.state || "unknown",
              commit: payload.commit_ref,
              pull_request_number: payload.pull_request || null,
              message: `Deploy ${payload.state === "success" ? "✅ succeeded" : "❌ failed"}`
            }
          }),
        });

        console.log("📤 Sent to GitHub:", ghRes.status);
      } catch (ghErr) {
        console.error("GitHub dispatch error:", ghErr);
      }
    }

    // Try to connect to Forge manifest for sovereign ledger
    let ledgerStatus = null;
    try {
      const forgeResponse = await fetch(`${forgeRoot}/manifest/resolve?target=ledger`, {
        method: "GET",
      });

      if (forgeResponse.ok) {
        const forgeData = await forgeResponse.json();
        const { ledger_url, ledger_signature, ledger_identity } = forgeData;

        // Prepare sovereign ledger payload
        const ledgerPayload = {
          timestamp: new Date().toISOString(),
          commit_ref: payload.commit_ref || null,
          deploy_state: payload.state || "unknown",
          bridge: "sr-aibridge",
          dominion: forgeRoot,
          relay: "netlify",
          verified_by: ledger_identity,
        };

        // Post event to the dynamically provisioned ledger URL
        const res = await fetch(ledger_url, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-Ledger-Signature": ledger_signature,
          },
          body: JSON.stringify(ledgerPayload),
        });

        ledgerStatus = res.status;
        console.log("📜 Sovereign ledger response:", ledgerStatus);
      }
    } catch (forgeErr) {
      console.log("ℹ️  Forge ledger not available:", forgeErr.message);
    }

    // Return to Bridge runtime
    return {
      statusCode: 200,
      body: JSON.stringify({
        result: "Bridge sync completed",
        forge: forgeRoot,
        ledgerStatus: ledgerStatus,
        timestamp: new Date().toISOString(),
      }),
    };
  } catch (err) {
    console.error("🔥 Bridge error:", err);
    return {
      statusCode: 500,
      body: JSON.stringify({ error: "Bridge internal error", message: err.message }),
    };
  }
}
