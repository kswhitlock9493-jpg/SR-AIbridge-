/**
 * Endpoint Bootstrap Utility
 * Handles endpoint retries, degradation recovery, and diagnostics dispatch
 */

const ENDPOINTS = ['/api/status', '/api/diagnostics', '/api/agents'];

export async function bootstrapEndpoints(baseUrl, onHealthUpdate) {
  const results = {};
  const timeout = ms => new Promise(res => setTimeout(res, ms));

  for (const endpoint of ENDPOINTS) {
    const url = `${baseUrl}${endpoint}`;
    let success = false;
    let attempt = 0;

    while (!success && attempt < 3) {
      attempt++;
      try {
        const res = await fetch(url);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        success = true;
        results[endpoint] = 'OK';
      } catch (err) {
        results[endpoint] = `Failed: ${err.message}`;
        await timeout(attempt * 2000);
      }
    }
  }

  const failed = Object.entries(results).filter(([, v]) => v.startsWith('Failed'));
  const status = failed.length ? 'DEGRADED' : 'HEALTHY';

  if (typeof onHealthUpdate === 'function')
    onHealthUpdate({ status, failedEndpoints: failed.map(f => f[0]) });

  try {
    await fetch(`${baseUrl}/api/diagnostics`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        type: status === 'HEALTHY' ? 'DEPLOYMENT_RECOVERY' : 'ENDPOINT_FAILURE',
        status,
        source: 'CommandDeck',
        meta: { failedEndpoints: failed.map(f => f[0]), timestamp: new Date().toISOString() }
      })
    });
  } catch (_) {
    // Silently fail diagnostic submission
  }

  return { status, results };
}
