/**
 * AgentMetricsTable - Display agent health and win rates
 */

export default function AgentMetricsTable({ metrics }) {
  const agents = Object.keys(metrics.winRates || {});

  if (agents.length === 0) {
    return (
      <div className="card">
        <h3>🤖 Agent Metrics</h3>
        <p className="empty-state">No agent data available</p>
      </div>
    );
  }

  return (
    <div className="card">
      <h3>🤖 Agent Metrics</h3>
      <table className="metrics-table">
        <thead>
          <tr>
            <th>Agent</th>
            <th>Win Rate</th>
            <th>Health</th>
          </tr>
        </thead>
        <tbody>
          {agents.map(agent => (
            <tr key={agent}>
              <td>{agent}</td>
              <td>{((metrics.winRates[agent] || 0) * 100).toFixed(1)}%</td>
              <td>
                <span className={`health-indicator ${getHealthClass(metrics.health[agent])}`}>
                  {((metrics.health[agent] || 0) * 100).toFixed(0)}%
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function getHealthClass(health) {
  if (!health) return 'unknown';
  if (health > 0.8) return 'good';
  if (health > 0.5) return 'fair';
  return 'poor';
}
