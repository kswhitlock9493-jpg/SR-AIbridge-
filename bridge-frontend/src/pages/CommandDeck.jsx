/**
 * CommandDeck - Self-Healing Deployment Monitor
 * Auto-checks backend health on load and updates UI dynamically
 */

import { useEffect, useState } from 'react';
import { bootstrapEndpoints } from '../utils/endpointBootstrap';

export default function CommandDeck() {
  const [status, setStatus] = useState('LOADING');
  const [failed, setFailed] = useState([]);
  const apiBase = import.meta.env.VITE_API_BASE || '/api';

  useEffect(() => {
    (async () => {
      const { status: healthStatus, results } = await bootstrapEndpoints(apiBase, ({ status, failedEndpoints }) => {
        setStatus(status);
        setFailed(failedEndpoints);
      });
      setStatus(healthStatus);
      setFailed(Object.entries(results).filter(([_, v]) => v.startsWith('Failed')).map(f => f[0]));
    })();
  }, [apiBase]);

  return (
    <div className="deck">
      <h1>SR-AIbridge Command Deck</h1>
      <p>Status: <strong>{status}</strong></p>
      {failed.length > 0 && (
        <div className="error-box">
          <strong>{failed.length}</strong> endpoint(s) failed:
          <ul>{failed.map(ep => <li key={ep}>{ep}</li>)}</ul>
        </div>
      )}
    </div>
  );
}
